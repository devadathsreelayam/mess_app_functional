from flask import Flask, render_template, jsonify, redirect, url_for, request
import pymysql
import datetime
import calendar

import queries
import database as db

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='mess'
    )


def get_first_and_last_dates(month_name, year):
    # Convert the month name to a number (1-12)
    month_number = list(calendar.month_name).index(month_name)

    if month_number == 0:
        raise ValueError("Invalid month name")

    # Get the first date of the month
    first_date = datetime.datetime(year, month_number, 1).date()

    # Get the last day of the month
    last_day = calendar.monthrange(year, month_number)[1]
    last_date = datetime.datetime(year, month_number, last_day).date()

    return first_date, last_date

@app.route('/')
def index():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return redirect(url_for('get_by_date', date=today))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/log_meals')
def log_meals():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return redirect(url_for('get_by_date', date=today))

@app.route('/summery', methods=['GET'])
def summery():
    if not request.args:
        return render_template('summery.html')

    # Extract the 'choose-type' parameter from the query string
    choose_type = request.args.get('choose-type')

    # Handle based on 'choose-type'
    if choose_type == 'date':
        # Get the 'date' parameter
        date = request.args.get('date')
        if date:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM inmates;')
            inmate_count = cursor.fetchone()[0]

            cursor.execute(
                """SELECT COUNT(breakfast), COUNT(lunch), COUNT(dinner) FROM mess_logs
                WHERE log_date = %s;""", (date,)
            )
            result = cursor.fetchone()
            breakfast = result[0]
            lunch = result[1]
            dinner = result[2]

            cursor.execute("SELECT COUNT(*) FROM mess_status WHERE in_status = 'in' AND update_date = %s;", (date,))
            join_count = cursor.fetchone()[0]

            cursor.close()

            return render_template('daily_summery.html', summery_date=date, brekfast_count=breakfast, lunch_count=lunch, dinner_count=dinner, join_count=join_count, inmate_count=inmate_count)
        else:
            return jsonify({'error': 'Date is required for date-based requests'}), 400

    elif choose_type == 'month':
        # Get the 'month' and 'year' parameters
        month = request.args.get('month')
        year = request.args.get('year')
        if month and year:
            first_date, last_date = get_first_and_last_dates(month, int(year))
            connection = get_db_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            cursor.execute(queries.monthly_summery_query, (first_date, last_date))

            result = cursor.fetchall()
            cursor.close()

            return render_template('monthly_summery.html', month=month, year=year, result=result)
        else:
            return jsonify({'error': 'Month and year are required for month-based requests'}), 400

    # If 'choose-type' is invalid or not provided
    return jsonify({'error': 'Invalid or missing choose-type parameter'}), 400

# Fixed route definition: use <string:date> instead of <str:date>
@app.route('/get_by_date/<string:date>', methods=['GET'])
def get_by_date(date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Fetch all inmate details and their statuses
        cursor.execute(
            """
            SELECT i.*, 
                   COALESCE(ms.update_date, %s) AS update_date,
                   COALESCE(ms.in_status, (
                       SELECT in_status
                       FROM mess_status ms2
                       WHERE ms2.mess_no = i.mess_no AND ms2.update_date <= %s
                       ORDER BY ms2.update_date DESC
                       LIMIT 1
                   )) AS in_status,
                   ml.breakfast, ml.lunch, ml.dinner
            FROM inmates i
            LEFT JOIN mess_status ms ON i.mess_no = ms.mess_no AND ms.update_date = %s
            LEFT JOIN mess_logs ml ON i.mess_no = ml.mess_no AND ml.log_date = %s
            WHERE %s >= i.join_date;
            """,
            (date, date, date, date, date)
        )
        inmates = cursor.fetchall()
        cursor.close()
        return render_template('log_meals.html', inmates=inmates, selected_date=date)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/get_inmate_details/<int:inmate_id>', methods=['GET'])
def get_inmate_details(inmate_id):
    # Get date from the request
    date = request.args.get('date')

    if not date:
        return jsonify({'error': 'Date is required'}), 400

    # Fetch inmate details from the database
    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            """SELECT i.*, m.in_status, ml.breakfast, ml.lunch, ml.dinner, gl.guest_count, gl.sg_count
                FROM inmates i
                LEFT JOIN mess_status m ON i.mess_no = m.mess_no AND m.update_date = %s
                LEFT JOIN mess_logs ml ON i.mess_no = ml.mess_no AND ml.log_date = %s
                LEFT JOIN guest_logs gl ON i.mess_no = gl.mess_no AND gl.log_date = %s
                WHERE i.mess_no = %s;""", (date, date, date, inmate_id)
        )
        inmate = cursor.fetchone()

    connection.close()

    # Return the inmate details as JSON response
    if inmate:
        return jsonify({
            'name': inmate['inmate_name'],
            'department': inmate['department'],
            'mess_number': inmate['mess_no'],
            'is_ablc': inmate['is_ablc'],
            'status': inmate['in_status'],
            'breakfast': inmate['breakfast'] if inmate['breakfast'] is not None else 0,
            'lunch': inmate['lunch'] if inmate['lunch'] is not None else 0,
            'dinner': inmate['dinner'] if inmate['lunch'] is not None else 0,
            'guest_count': inmate['guest_count'],
            'sg_count': inmate['sg_count'],
        })
    else:
        return jsonify({'error': 'Inmate not found'}), 404


@app.route('/update_inmate_status', methods=['POST'])
def update_inmate_status():
    try:
        data = request.get_json()  # Receive data as JSON
        mess_no = data.get('mess_number')
        date = data.get('date')
        status = data.get('status')
        breakfast = data.get('breakfast')
        lunch = data.get('lunch')
        dinner = data.get('dinner')
        guest_count = data.get('guest_count')
        sg_count = data.get('sg_count')

        connection = get_db_connection()
        cursor = connection.cursor()

        # Update or insert into mess_status
        cursor.execute(
            """INSERT INTO mess_status (mess_no, update_date, in_status)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE in_status = VALUES(in_status);""",
            (mess_no, date, status)
        )

        # Update or insert into mess_logs
        cursor.execute(
            """INSERT INTO mess_logs (mess_no, log_date, breakfast, lunch, dinner) 
               VALUES (%s, %s, %s, %s, %s) 
               ON DUPLICATE KEY UPDATE breakfast = VALUES(breakfast), 
                                       lunch = VALUES(lunch), 
                                       dinner = VALUES(dinner);""",
            (mess_no, date, breakfast, lunch, dinner)
        )

        # Update or insert into guest_logs
        cursor.execute(
            """INSERT INTO guest_logs (mess_no, log_date, guest_count, sg_count) 
               VALUES (%s, %s, %s, %s) 
               ON DUPLICATE KEY UPDATE guest_count = VALUES(guest_count), 
                                       sg_count = VALUES(sg_count);""",
            (mess_no, date, guest_count, sg_count)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Status and meals updated successfully!'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to update inmate status.'}), 500

@app.route('/add_inmate')
def add_inmate():
    return render_template('add_inmate.html')

@app.route('/save_inmate', methods=['POST'])
def save_inmate():
    try:
        mess_no = request.form.get('mess_no')
        name = request.form.get('inmate_name')
        department = request.form.get('department')
        ablc = request.form.get('ablc')
        join_date = request.form.get('join_date')

        ablc = 1 if ablc == 'ablc' else 0

        print(mess_no, name, department, ablc, join_date)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO inmates (mess_no, inmate_name, department, is_ablc, join_date)
               VALUES (%s, %s, %s, %s, %s);""", (mess_no, name, department, ablc, join_date)
        )

        cursor.execute(
            """INSERT INTO mess_status (mess_no, update_date, in_status)
               VALUES (%s, CURDATE(), %s);""", (mess_no, 'out')
        )

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('add_inmate'))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to save inmate record.'}), 500
    

@app.route('/manage_inmates')
def manage_inmates():
    inmates = db.view_all_inmates()
    print(inmates)
    
    if inmates:
        return render_template('view_inmates.html', inmates=inmates)


@app.route('/get_inmate/<int:inmate_id>', methods=['GET'])
def get_inmate(inmate_id):
    # Fetch inmate details from the database
    connection = get_db_connection()
    inmate = db.get_inmate(inmate_id)
    connection.close()

    # Return the inmate details as JSON response
    if inmate:
        return jsonify({
            'name': inmate['inmate_name'],
            'department': inmate['department'],
            'mess_number': inmate['mess_no'],
            'is_ablc': inmate['is_ablc'],
            'join_date': datetime.datetime.strftime(inmate['join_date'], '%Y-%m-%d')
        })
    else:
        return jsonify({'error': 'Inmate not found'}), 404

@app.route('/update_inmate', methods=['POST'])
def update_inmate():
    try:
        mess_no = request.form.get('mess_no')
        name = request.form.get('inmate_name')
        department = request.form.get('department')
        ablc = request.form.get('ablc')
        ablc = 1 if ablc == 'ablc' else 0

        if db.update_inmate(mess_no, name, department, ablc):
            return redirect(url_for('manage_inmates'))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to save inmate record.'}), 500


@app.route('/delete_inmate/<int:inmate_id>', methods=['GET'])
def delete_inmate(inmate_id):
    try:
        success = db.delete_inmate(inmate_id)  # Ensure this method is correctly implemented
        if success:
            return redirect(url_for('manage_inmates'))
        else:
            return jsonify({"error": "Inmate not found"}), 404
    except Exception as e:
        # Log the exception for debugging
        print(f"Error deleting inmate: {e}")
        return jsonify({"error": "An error occurred while deleting inmate."}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
