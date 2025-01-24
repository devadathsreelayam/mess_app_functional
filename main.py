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
        cursor.execute("SELECT i.*, m.in_status FROM inmates i LEFT JOIN mess_status m USING (mess_no) WHERE m.update_date = %s", (date,))
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
    with connection.cursor() as cursor:
        cursor.execute('SELECT i.*, m.in_status FROM inmates i LEFT JOIN mess_status m USING(mess_no) WHERE mess_no = %s AND m.update_date = %s', (inmate_id, date))
        inmate = cursor.fetchone()

    connection.close()

    # Return the inmate details as JSON response
    if inmate:
        return jsonify({
            'name': inmate[0],
            'department': inmate[1],
            'mess_number': inmate[2],
            'is_ablc': inmate[3],
            'status': inmate[4],
        })
    else:
        return jsonify({'error': 'Inmate not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
