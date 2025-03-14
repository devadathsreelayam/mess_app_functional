from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import User
from . import db, role_required


auth = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'static/images/users'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=False)
            return redirect(url_for('views.index'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/manage_users')
@login_required
@role_required('admin', 'secretary')
def manage_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@auth.route('/get_user', methods=['POST'])
@login_required
def get_user():
    try:
        data = request.get_json()  # Extract JSON data
        if not data or 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400

        user_id = data['user_id']
        user = User.query.get(user_id)  # Fetch user from the database

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user.id,
            'email': user.email,
            'user_name': user.user_name,
            'department': user.department,
            'mobile': user.mobile,
            'active_status': user.active_status.value,
            'role': user.role
        })

    except Exception as e:
        print(f'Error fetching user: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500


@auth.route('/add_user', methods=['POST'])
@login_required
def add_user():
    try:
        # Retrieve form data
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))
        user_name = request.form.get('user_name')
        department = request.form.get('department')
        mobile = request.form.get('mobile')
        role = request.form.get('role')

        # Create the user without committing yet (to get the user ID)
        user = User(
            email=email,
            user_name=user_name,
            password=password,
            department=department,
            mobile=mobile,
            role=role,
            added_date=datetime.now(),
            last_edit=datetime.now(),
            added_by=current_user.id
        )

        db.session.add(user)
        db.session.flush()  # Flush to get user.id before commit
        print(f'User created with ID: {user.id}')

        db.session.commit()  # Final commit after processing image
        print('User added and data committed successfully.')

        return redirect(url_for('auth.manage_users'))

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f'Error occurred while adding new user: {e}')
        return jsonify({'error': 'Failed to save new user.'}), 500


@auth.route('/update_user', methods=['POST'])
@login_required
def update_user():
    try:
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found.'}), 404

        user.email = request.form.get('email')
        user.password = generate_password_hash(request.form.get('password'))
        user.user_name = request.form.get('user_name')
        user.department = request.form.get('department')
        user.mobile = request.form.get('mobile')
        user.role = request.form.get('role')
        user.last_edit = datetime.now()
        user.edited_by = current_user.id

        db.session.commit()
        return redirect(url_for('auth.manage_users'))

    except Exception as e:
        print(f'Error occurred while adding new user: {e}')
        return jsonify({'error': 'Failed to save new user.'}), 500