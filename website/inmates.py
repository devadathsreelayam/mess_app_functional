from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy.sql import text
from datetime import datetime

from .models import Inmate, Bill
from . import db, role_required
from .utils import get_first_and_last_dates

inmates = Blueprint('inmates' ,__name__)


@inmates.route('/manage_inmates')
@login_required
@role_required('admin', 'secretary')
def manage_inmates():
    inmates_list = Inmate.query.order_by('mess_no').all()
    return render_template('view_inmates.html', inmates=inmates_list, current_user=current_user)

@inmates.route('/inmate_login')
def inmate_login():
    return render_template('inmate_login.html')


@inmates.route('/inmate_redirect')
def inmate_redirect():
    mess_no = request.args.get('mess_no')
    inmate = Inmate.query.filter_by(mess_no=mess_no).first()
    return redirect(url_for('inmates.inmate_dash', inmate_id=inmate.inmate_id))


@inmates.route('/save_inmate', methods=['POST'])
@login_required
@role_required('admin', 'secretary')
def save_inmate():
    try:
        mess_no = request.form.get('mess_no')
        name = request.form.get('inmate_name')
        department = request.form.get('department')
        ablc = request.form.get('ablc')
        join_date = request.form.get('join_date')

        ablc = 1 if ablc == 'ablc' else 0
        last_edit = datetime.now()
        edited_by = current_user.id

        inmate = Inmate(mess_no=mess_no, inmate_name=name, department=department, is_ablc=ablc, join_date=join_date, last_edit=last_edit, edited_by=edited_by)
        db.session.add(inmate)
        db.session.commit()

        return redirect(url_for('inmates.manage_inmates'))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to save inmate record.'}), 500


@inmates.route('/get_inmate/<int:inmate_id>', methods=['GET'])
@login_required
@role_required('admin', 'secretary')
def get_inmate(inmate_id):
    # Fetch inmate details from the database
    inmate = Inmate.query.filter_by(inmate_id=inmate_id).first()

    # Return the inmate details as JSON response
    if inmate:
        return jsonify({
            'inmate_id': inmate.inmate_id,
            'name': inmate.inmate_name,
            'department': inmate.department,
            'mess_number': inmate.mess_no,
            'is_ablc': inmate.is_ablc,
            'join_date': datetime.strftime(inmate.join_date, '%Y-%m-%d')
        })
    else:
        return jsonify({'error': 'Inmate not found'}), 404


@inmates.route('/update_inmate', methods=['POST'])
@login_required
@role_required('admin', 'secretary')
def update_inmate():
    try:
        inmate_id = request.form.get('inmate_id')
        mess_no = request.form.get('mess_no')
        name = request.form.get('inmate_name')
        department = request.form.get('department')
        ablc = request.form.get('ablc')
        ablc = 1 if ablc == 'ablc' else 0

        inmate = Inmate.query.get(inmate_id)
        inmate.mess_no = mess_no
        inmate.inmate_name = name
        inmate.department = department
        inmate.is_ablc = ablc

        db.session.commit()
        return redirect(url_for('inmates.manage_inmates'))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to save inmate record.'}), 500


@login_required
@role_required('admin', 'secretary')
@inmates.route('/delete_inmate/<int:inmate_id>', methods=['DELETE'])
def delete_inmate(inmate_id):
    try:
        inmate = Inmate.query.get(inmate_id)
        if inmate:
            db.session.delete(inmate)
            db.session.commit()  # Commit the deletion to the database
            return jsonify({"message": f"Inmate with ID {inmate_id} deleted successfully."}), 200
        else:
            return jsonify({"error": "Inmate not found"}), 404
    except Exception as e:
        # Log the exception for debugging
        print(f"Error deleting inmate: {e}")
        return jsonify({"error": "An error occurred while deleting inmate."}), 500


@inmates.route('/inmate_view/<int:inmate_id>')
@login_required
def inmate_view(inmate_id):
    try:
        inmate = Inmate.query.get(inmate_id)
        bills = Bill.query.filter_by(inmate_id=inmate_id)
        days_info = get_days_info()
        return render_template('inmate_view.html', inmate=inmate, bills=bills, days_info=days_info, current_user=current_user)
    except Exception as e:
        print(f'Some error occurred: {e}')
        return jsonify({"error": "An error occurred while opening inmate view."}), 500


@inmates.route('/inmate_dash/<int:inmate_id>')
def inmate_dash(inmate_id):
    try:
        inmate = Inmate.query.get(inmate_id)
        bills = Bill.query.filter_by(inmate_id=inmate_id)
        days_info = get_days_info()
        return render_template('inmate_dash.html', inmate=inmate, bills=bills, days_info=days_info)
    except Exception as e:
        print(f'Some error occurred: {e}')
        return jsonify({"error": "An error occurred while opening inmate view."}), 500


def get_days_info():
    join_data = db.session.execute(
        text("SELECT * FROM bills_generated WHERE is_generated ORDER BY year, month DESC LIMIT 1;")
    ).fetchone()
    if not join_data:
        start_month = 1
        start_year = 2025
    else:
        start_year, start_month, _ = join_data
        start_year += 1
        start_month += 1

    current_date = datetime.now()
    current_month, current_year = current_date.month, current_date.year

    months = []
    year, month = start_year, start_month

    while (year < current_year) or (year == current_year and month <= current_month):
        months.append((month, year))
        month += 1
        if month > 12:  # Move to next year
            month = 1
            year += 1

    return months


@inmates.route('/change_bill_status', methods=['POST'])
@login_required
@role_required('admin', 'secretary')
def change_bill_status():
    data = request.get_json()
    inmate_id = data.get('inmate_id')
    month = data.get('month')
    year = data.get('year')

    # Fetch the bill object
    bill = Bill.query.filter_by(inmate_id=inmate_id, month=month, year=year).first()
    inmate = Inmate.query.get(inmate_id)

    # Check if bill exists
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404

    # Update status only if it's not already 'Due'
    if bill.status != 'Due':
        bill.status = 'Due'
        inmate.is_bill_due += 1
        db.session.commit()
        return jsonify({'message': 'Bill status updated successfully'}), 200
    else:
        return jsonify({'message': 'Bill status was already "Due"'}), 200


@inmates.route('/update_bill_paid', methods=['POST'])
@login_required
@role_required('admin', 'secretary')
def update_bill_paid():
    data = request.get_json()
    inmate_id = data.get('inmate_id')
    month = data.get('month')
    year = data.get('year')
    paid_date = data.get('paid_date')
    reference_id = data.get('reference_id')

    # Fetch the bill object
    bill = Bill.query.filter_by(inmate_id=inmate_id, month=month, year=year).first()
    inmate = Inmate.query.get(inmate_id)

    # Check if bill exists
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404

    # Update status only if it's not already 'Due'
    if bill.status != 'Paid':
        bill.status = 'Paid'
        bill.paid_date = paid_date
        bill.reference_id = reference_id

        if inmate.is_bill_due != 0:
            inmate.is_bill_due -= 1
        db.session.commit()
        return jsonify({'message': 'Bill status updated successfully'}), 200
    else:
        return jsonify({'message': 'Bill status was already "Paid"'}), 200


@inmates.route('/show_joins', methods=['GET'])
@login_required
@role_required('admin', 'secretary', 'steerer')
def show_joins():
    inmate_id = request.args.get('inmateId')
    try:
        month = int(request.args.get('month'))
        year = int(request.args.get('year'))
    except TypeError:
        return jsonify({'message': 'some error occurred'})

    first_date, last_date = get_first_and_last_dates(month, year)
    query = """
        SELECT ms.update_date, ms.in_status, ml.breakfast, ml.lunch, ml.dinner, gl.guest_count, gl.sg_count
        FROM mess_status ms
        LEFT JOIN meals_log ml USING (update_date, inmate_id)
        LEFT JOIN guest_log gl USING (update_date, inmate_id)
        WHERE ms.inmate_id = :inmate_id AND ms.update_date BETWEEN :start_date AND :last_date
        ORDER BY ms.update_date ASC;
    """
    joins = db.session.execute(text(query), {'inmate_id': inmate_id, 'start_date': first_date, 'last_date': last_date}).fetchall()

    # Convert the result to a list of dictionaries
    result = []
    total_mess_in_days = 0
    total_guest_count = 0
    total_sg_count = 0

    for row in joins:
        is_mess_in = bool(row.in_status)
        if is_mess_in:
            total_mess_in_days += 1
        total_guest_count += row.guest_count if row.guest_count is not None else 0
        total_sg_count += row.sg_count if row.sg_count is not None else 0

        result.append({
            'update_date': datetime.strftime(row.update_date, '%d-%m-%Y'),
            'in_status': 'Mess In' if row.in_status else 'Mess Out',
            'guest_count': row.guest_count,
            'sg_count': row.sg_count
        })

    # Append total row
    result.append({
        'update_date': 'Total',
        'in_status': total_mess_in_days,
        'guest_count': total_guest_count,
        'sg_count': total_sg_count
    })

    # Return the result as JSON
    return jsonify(result)

