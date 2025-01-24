from flask import Flask, render_template, jsonify, redirect, url_for, request
import pymysql
import datetime

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='mess'
    )

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/log_meals')
def log_meals():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return redirect(url_for('get_by_date', date=today))

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
            LEFT JOIN mess_logs ml ON i.mess_no = ml.mess_no AND ml.log_date = %s;
            """,
            (date, date, date, date)
        )
        inmates = cursor.fetchall()
        cursor.close()
        return render_template('index.html', inmates=inmates, selected_date=date)
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
            """SELECT i.*, m.in_status, ml.breakfast, ml.lunch, ml.dinner
               FROM inmates i
               LEFT JOIN mess_status m ON i.mess_no = m.mess_no AND m.update_date = %s
               LEFT JOIN mess_logs ml ON i.mess_no = ml.mess_no AND ml.log_date = %s
               WHERE i.mess_no = %s;""", (date, date, inmate_id)
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

        connection = get_db_connection()
        cursor = connection.cursor()

        # Update mess status
        try:
            cursor.execute(
                """UPDATE mess_status
                SET in_status = %s
                WHERE mess_no = %s AND update_date = %s;""", (status, mess_no, date)
            )
        except Exception:
            cursor.execute(
                """INSERT INTO mess_status (mess_no, update_date, in_status) 
                   VALUES (%s, %s, %s) 
                   ON DUPLICATE KEY UPDATE in_status = VALUES(in_status);""",
                (mess_no, date, status)
            )

        # Update meals
        cursor.execute(
            """INSERT INTO mess_logs (mess_no, log_date, breakfast, lunch, dinner) 
               VALUES (%s, %s, %s, %s, %s) 
               ON DUPLICATE KEY UPDATE breakfast = VALUES(breakfast), 
                                       lunch = VALUES(lunch), 
                                       dinner = VALUES(dinner);""",
            (mess_no, date, breakfast, lunch, dinner)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Status and meals updated successfully!'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to update inmate status.'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
