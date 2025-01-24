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
    today = datetime.date.today().strftime("%Y-%m-%d")
    return redirect(url_for('get_by_date', date=today))

# Fixed route definition: use <string:date> instead of <str:date>
@app.route('/get_by_date/<string:date>', methods=['GET'])
def get_by_date(date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            """SELECT i.*, ms.update_date, ms.in_status, ml.breakfast, ml.lunch, ml.dinner
                FROM inmates i
                LEFT JOIN mess_status ms ON i.mess_no = ms.mess_no AND ms.update_date = %s
                LEFT JOIN mess_logs ml ON i.mess_no = ml.mess_no AND ml.log_date = %s;""", (date, date)
        )
        inmates = cursor.fetchall()
        cursor.close()
        return render_template('index.html', inmates=inmates, selected_date=date)
    except:
        return "Some error occurred!"

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
