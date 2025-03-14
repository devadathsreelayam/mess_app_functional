from flask import Blueprint, request, redirect, url_for, render_template, jsonify, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import User, UserActiveStatus
from . import db, role_required

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.active_status != UserActiveStatus.ACTIVE:
                flash("Your account is not active. Please contact the administrator.", "danger")
                return redirect(url_for('auth.login'))

            if check_password_hash(user.password, password):
                login_user(user, remember=False)
                return redirect(url_for('views.index'))

        flash("Invalid email or password.", "danger")

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
@role_required('admin', 'secretary')
def get_user():
    """Fetches user details securely. Only admin or the user can access."""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400

        user_id = data['user_id']

        # Restrict access to admin or the user themselves
        if current_user.role not in ['admin', 'secretary'] and current_user.id != int(user_id):
            return jsonify({'error': 'Unauthorized'}), 403

        user = User.query.get(user_id)
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
@role_required('admin', 'secretary')
def add_user():
    """Adds a new user after validating inputs."""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        user_name = request.form.get('user_name')
        department = request.form.get('department')
        mobile = request.form.get('mobile')
        role = request.form.get('role')

        # Validate input
        if not email or not password or not user_name or not department or not mobile or not role:
            flash("All fields are required!", "danger")
            return redirect(url_for('auth.manage_users'))

        if User.query.filter_by(email=email).first():
            flash("Email is already in use!", "danger")
            return redirect(url_for('auth.manage_users'))

        if User.query.filter_by(mobile=mobile).first():
            flash("Mobile number is already in use!", "danger")
            return redirect(url_for('auth.manage_users'))

        hashed_password = generate_password_hash(password)

        user = User(
            email=email,
            user_name=user_name,
            password=hashed_password,
            department=department,
            mobile=mobile,
            role=role,
            added_date=datetime.now(),
            last_edit=datetime.now(),
            added_by=current_user.id
        )

        db.session.add(user)
        db.session.commit()

        flash("User added successfully!", "success")
        return redirect(url_for('auth.manage_users'))

    except Exception as e:
        db.session.rollback()
        print(f'Error occurred while adding new user: {e}')
        flash("Failed to save new user.", "danger")
        return redirect(url_for('auth.manage_users'))


@auth.route('/update_user', methods=['POST'])
@login_required
@role_required('admin', 'secretary')
def update_user():
    """Updates user details securely."""
    try:
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)

        if not user:
            flash("User not found!", "danger")
            return redirect(url_for('auth.manage_users'))

        user.email = request.form.get('email')
        user.user_name = request.form.get('user_name')
        user.department = request.form.get('department')
        user.mobile = request.form.get('mobile')
        user.role = request.form.get('role')
        user.last_edit = datetime.now()
        user.edited_by = current_user.id
        user.active_status = UserActiveStatus[request.form.get('active_status').upper()]

        # Only update the password if a new one is provided
        new_password = request.form.get('password')
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("User updated successfully!", "success")
        return redirect(url_for('auth.manage_users'))

    except Exception as e:
        db.session.rollback()
        print(f'Error occurred while updating user: {e}')
        flash("Failed to update user.", "danger")
        return redirect(url_for('auth.manage_users'))
