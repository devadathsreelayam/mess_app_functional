from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user

from . import db, role_required
from sqlalchemy.sql import text
from .models import Inmate, MessStatus, MealsLog, GuestLog, Expense
from datetime import datetime, date

views = Blueprint('views' ,__name__)

@views.route('/')
@login_required
def index():
    today = date.today().strftime("%Y-%m-%d")
    return redirect(url_for('views.get_by_date', date=today))

@views.route('/log_meals')
@login_required
def log_meals():
    today = date.today().strftime("%Y-%m-%d")
    return redirect(url_for('views.get_by_date', date=today))


@views.route('/manage_expense')
@login_required
@role_required('admin', 'secretary', 'steerer')
def manage_expense():
    expenses = db.session.execute(text(
            """SELECT e.*, u.user_name FROM expense e
            JOIN user u ON e.added_by = u.id
            ORDER BY e.bill_date DESC;"""
        )).fetchall()

    return render_template('manage_expense.html', expenses=expenses)


@views.route('/add_expense', methods=['POST'])
@login_required
@role_required('admin', 'secretary')
def add_expense():
    expense_name = request.form.get('expense_name')
    bill_date = request.form.get('bill_date')
    shop_name = request.form.get('shop_name')
    expense_type = request.form.get('expense_type')
    expense_category = request.form.get('expense_category')
    bill_amount = request.form.get('bill_amount')

    expense = Expense(
        note=expense_name,
        bill_date=bill_date,
        shop=shop_name,
        added_by=current_user.id,
        type=expense_type,
        category=expense_category,
        amount=bill_amount,
        last_edit=datetime.now()
    )

    db.session.add(expense)
    db.session.commit()

    return redirect(url_for('views.manage_expense'))


@views.route('/get_expense/<int:expense_id>', methods=['GET'])
@login_required
@role_required('admin', 'secretary')
def get_expense(expense_id):
    expense = Expense.query.get(expense_id)  # Retrieve the expense by ID
    result = {
        'id': expense.id,
        'note': expense.note,
        'bill_date': expense.bill_date.strftime('%Y-%m-%d'),
        'shop': expense.shop,
        'type': expense.type.name.lower(),
        'category': expense.category,
        'amount': expense.amount,
    }
    return jsonify(result)


@views.route('/update_expense/<int:expense_id>', methods=['POST'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        expense_name = request.form.get('expense_name')
        bill_date = request.form.get('bill_date')
        shop_name = request.form.get('shop_name')
        expense_type = request.form.get('expense_type')
        expense_category = request.form.get('expense_category')
        bill_amount = request.form.get('bill_amount')

        expense.note = expense_name
        expense.bill_date = datetime.strptime(bill_date, '%Y-%m-%d')
        expense.shop = shop_name
        expense.type = expense_type
        expense.category = expense_category
        expense.amount = bill_amount
        expense.last_edit = datetime.now()
        expense.edited_by = current_user.id

        db.session.commit()
        return redirect(url_for('views.manage_expense'))


@views.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        expense = Expense.query.get(expense_id)  # Assuming SQLAlchemy ORM
        if not expense:
            return jsonify({"error": "Expense not found"}), 404

        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@views.route('/get_by_date/<string:date>', methods=['GET'])
@login_required
def get_by_date(date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()

        # Check and copy data if not available for the requested date
        if not is_data_available(date_obj):
            copy_data_from_previous_date(date_obj)

        # Fetch all inmate details and their statuses
        inmates = fetch_inmates_with_status(date_obj)
        return render_template('log_meals.html', inmates=inmates, selected_date=date)
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}", 500


def is_data_available(date):
    """Check if data is available for the given date."""
    return db.session.execute(
        text("SELECT * FROM status_initialization_log WHERE date = :date"),
        {'date': date}
    ).scalar()


def copy_data_from_previous_date(date):
    """Copy data from the previous available date to the given date."""
    prev_date = get_previous_available_date(date)
    if prev_date:
        # Copy mess_status data
        copy_mess_status_data(date, prev_date)
        # Mark the new date as available
        mark_data_as_available(date)
        db.session.commit()


def get_previous_available_date(date):
    """Get the previous available date from the data_availability table."""
    return db.session.execute(
        text("SELECT date FROM status_initialization_log WHERE date < :date ORDER BY date DESC LIMIT 1"),
        {'date': date}
    ).scalar()


def copy_mess_status_data(new_date, prev_date):
    """Copy mess_status data from the previous date to the new date."""
    copy_query = """
        INSERT IGNORE INTO mess_status (inmate_id, update_date, in_status, last_edit, edited_by)
        SELECT inmate_id, :new_date, in_status, :last_edit, :edited_by
        FROM mess_status
        WHERE update_date = :prev_date;
    """
    db.session.execute(text(copy_query), {'new_date': new_date, 'prev_date': prev_date, 'last_edit': datetime.now(), 'edited_by': current_user.id})


def mark_data_as_available(date):
    """Mark the given date as available in the data_availability table."""
    db.session.execute(
        text("INSERT INTO status_initialization_log (date) VALUES (:date)"),
        {'date': date}
    )


def fetch_inmates_with_status(date):
    """Fetch all inmate details and their statuses for the given date."""
    query = """
        SELECT i.*, m.in_status, ml.breakfast, ml.lunch, ml.dinner, gl.guest_count, gl.sg_count
        FROM inmate i
        LEFT JOIN mess_status m ON i.inmate_id = m.inmate_id AND m.update_date = :date
        LEFT JOIN meals_log ml ON i.inmate_id = ml.inmate_id AND ml.update_date = :date
        LEFT JOIN guest_log gl ON i.inmate_id = gl.inmate_id AND gl.update_date = :date
        WHERE :date >= i.join_date ORDER BY i.mess_no;
    """
    return db.session.execute(text(query), params={'date': date})


@views.route('/get_inmate_details/<int:inmate_id>', methods=['GET'])
@login_required
def get_inmate_details(inmate_id):
    # Get date from the request
    date = request.args.get('date')

    if not date:
        return jsonify({'error': 'Date is required'}), 400

    query = """SELECT i.*, m.in_status, ml.breakfast, ml.lunch, ml.dinner, gl.guest_count, gl.sg_count
                FROM inmate i
                LEFT JOIN mess_status m ON i.inmate_id = m.inmate_id AND m.update_date = :date
                LEFT JOIN meals_log ml ON i.inmate_id = ml.inmate_id AND ml.update_date = :date
                LEFT JOIN guest_log gl ON i.inmate_id = gl.inmate_id AND gl.update_date = :date
                WHERE i.inmate_id = :inmate_id;"""

    inmate = db.session.execute(text(query), params={'date': date, 'inmate_id': inmate_id}).fetchone()

    # Return the inmate details as JSON response
    if inmate:
        return jsonify({
            'name': inmate.inmate_name,
            'department': inmate.department,
            'mess_number': inmate.mess_no,
            'is_ablc': inmate.is_ablc,
            'status': inmate.in_status,
            'breakfast': inmate.breakfast if inmate.breakfast is not None else 0,
            'lunch': inmate.lunch if inmate.lunch is not None else 0,
            'dinner': inmate.dinner if inmate.lunch is not None else 0,
            'guest_count': inmate.guest_count,
            'sg_count': inmate.sg_count,
            'is_bill_due': inmate.is_bill_due,
        })
    else:
        return jsonify({'error': 'Inmate not found'}), 404


@views.route('/update_inmate_status', methods=['POST'])
def update_inmate_status():
    try:
        data = request.get_json()  # Receive data as JSON
        inmate_id = data.get('inmate_id')
        date = data.get('date')
        status = data.get('status')
        breakfast = bool(data.get('breakfast'))
        lunch = bool(data.get('lunch'))
        dinner = bool(data.get('dinner'))
        guest_count = data.get('guest_count')
        sg_count = data.get('sg_count')
        print(data)

        # Update mess in status
        # Obtain mess in status from table
        mess_status = MessStatus.query.get({'inmate_id': inmate_id, 'update_date': date})
        if mess_status.in_status and (breakfast or lunch or dinner):
            print('Attempt to mess out inmate with meals logged.')
            return jsonify({'message': 'Attempt to mess out inmate with meals logged.'})

        if mess_status:
            # If mess in status is available in the table, update
            mess_status.in_status = status
            mess_status.last_edit = datetime.now()
            mess_status.edited_by = current_user.id
            db.session.commit()
        else:
            # Create new mess status
            mess_status = MessStatus(
                inmate_id=inmate_id,
                update_date=date,
                in_status=status,
                last_edit=datetime.now(),
                edited_by=current_user.id
            )
            db.session.add(mess_status)
            db.session.commit()

        meals_log = MealsLog.query.get({'inmate_id': inmate_id, 'update_date': date})
        if meals_log:
            meals_log.breakfast = breakfast
            meals_log.lunch = lunch
            meals_log.dinner = dinner
            meals_log.last_edit = datetime.now()
            meals_log.edited_by = current_user.id
            db.session.commit()
        else:
            meals_log = MealsLog(
                inmate_id=inmate_id,
                update_date=date,
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                last_edit=datetime.now(),
                edited_by=current_user.id
            )
            db.session.add(meals_log)
            db.session.commit()

        guest_log = GuestLog.query.get({'inmate_id': inmate_id, 'update_date': date})
        if guest_log:
            guest_log.guest_count = guest_count
            guest_log.sg_count = sg_count
            guest_log.last_edit = datetime.now()
            guest_log.edited_by = current_user.id
            db.session.commit()
        else:
            guest_log = GuestLog(
                inmate_id=inmate_id,
                update_date=date,
                guest_count=guest_count,
                sg_count=sg_count,
                last_edit=datetime.now(),
                edited_by=current_user.id
            )
            db.session.add(guest_log)
            db.session.commit()

        return jsonify({'message': 'Status and meals updated successfully!'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to update inmate status.'}), 500
