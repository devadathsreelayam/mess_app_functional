from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required
from sqlalchemy.sql import text
from datetime import datetime
import pandas as pd

from .utils import get_first_and_last_dates
from . import db, role_required

summaries = Blueprint('summaries', __name__)


@summaries.route('/summery')
@login_required
def summery():
    daily_count = db.session.execute(
        text('SELECT COUNT(*) AS count FROM mess_status WHERE in_status AND update_date = CURRENT_DATE()')
    ).fetchone()
    return render_template('summery.html', daily_count=daily_count.count)


@summaries.route('/daily_summery', methods=['GET'])
def daily_summery():
    if not request.args:
        return redirect(url_for('summery'))

    date = request.args.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
        inmate_count = db.session.execute(
            text('SELECT COUNT(*) AS inmate_count FROM inmate WHERE join_date <= :date;'), params={'date': date}
        ).fetchone()

        query = """SELECT SUM(breakfast) AS breakfast, SUM(lunch) AS lunch, SUM(dinner) AS dinner
         FROM meals_log WHERE update_date = :date;"""
        meals_log = db.session.execute(text(query), params={'date': date}).fetchone()

        query = "SELECT COUNT(*) AS join_count FROM mess_status WHERE in_status AND update_date = :date;"
        mess_status = db.session.execute(text(query), params={'date': date}).fetchone()

        daily_report = {
            'summery_date': date.strftime('%B %d, %Y'),
            'breakfast_count': meals_log.breakfast,
            'lunch_count': meals_log.lunch,
            'dinner_count': meals_log.dinner,
            'join_count': mess_status.join_count,
            'inmate_count': inmate_count.inmate_count
        }
        daily_count = db.session.execute(
            text('SELECT COUNT(*) AS count FROM mess_status WHERE in_status AND update_date = CURRENT_DATE()')
        ).fetchone()

        return render_template('summery.html', daily_summery=daily_report, daily_count=daily_count.count)
    else:
        return jsonify({'error': 'Date is required for date-based requests'}), 400


@summaries.route('/bills')
@login_required
@role_required('admin', 'secretary')
def bills():
    return render_template('bills.html')


@summaries.route('/choose_month', methods=['GET'])
def choose_month():
    try:
        month = request.args.get('month')
        year = request.args.get('year')

        first_date, last_date = get_first_and_last_dates(month, int(year))
        inmates_summery = calculate_monthly_summery(first_date, last_date)

        expense_query = """
            SELECT type, SUM(amount) AS amount FROM expense
            WHERE bill_date BETWEEN :first_date AND :last_date
            GROUP BY type;
        """
        expense_summery = db.session.execute(text(expense_query), params={'first_date': first_date, 'last_date': last_date}).fetchall()

        return jsonify(inmates_summery.to_dict(orient='records'))

    except Exception as e:
        print(f'Error while fetching monthly data: {e}')
        return jsonify({'error': 'Error obtaining monthly data'}), 400


def calculate_monthly_summery(first_date, last_date):
    query = """
            WITH mess_status_summary AS (
                SELECT inmate_id, COALESCE(SUM(in_status), 0) AS join_count
                FROM mess_status
                WHERE update_date BETWEEN :first_date AND :last_date
                GROUP BY inmate_id
            ),
            guest_log_summary AS (
                SELECT inmate_id, COALESCE(SUM(guest_count), 0) AS total_guest_count, COALESCE(SUM(sg_count), 0) AS total_sg_count
                FROM guest_log
                GROUP BY inmate_id
            )
            SELECT 
                i.inmate_id, 
                i.mess_no, 
                i.inmate_name, 
                i.department, 
                i.is_ablc, 
                COALESCE(mss.join_count, 0) AS join_count, 
                COALESCE(gls.total_guest_count, 0) AS total_guest_count, 
                COALESCE(gls.total_sg_count, 0) AS total_sg_count
            FROM inmate i
            LEFT JOIN mess_status_summary mss ON i.inmate_id = mss.inmate_id
            LEFT JOIN guest_log_summary gls ON i.inmate_id = gls.inmate_id
            WHERE i.join_date <= :last_date;
        """

    # Execute the query and load the results into a Pandas DataFrame
    df = pd.read_sql_query(
        text(query),
        db.engine,  # Use the SQLAlchemy engine from your Flask app
        params={'first_date': first_date, 'last_date': last_date}
    )

    df['inmate_id'] = df['inmate_id'].astype(int)
    df['mess_no'] = df['mess_no'].astype(int)
    df['is_ablc'] = df['is_ablc'].astype(bool)
    df['join_count'] = df['join_count'].astype(int)
    df['total_guest_count'] = df['total_guest_count'].astype(int)
    df['total_sg_count'] = df['total_sg_count'].astype(int)

    # Add a total row
    total_row = {
        'inmate_id': 'Total',
        'mess_no': '',
        'inmate_name': '',
        'department': '',
        'is_ablc': '',
        'join_count': df['join_count'].sum(),  # Sum of join_count
        'total_guest_count': df['total_guest_count'].sum(),  # Sum of total_guest_count
        'total_sg_count': df['total_sg_count'].sum()  # Sum of total_sg_count
    }

    df.loc['total'] = total_row

    return df