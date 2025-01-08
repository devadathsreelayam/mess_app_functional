from flask import Flask, render_template
import pymysql

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
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT i.*, m.in_status FROM inmates i LEFT JOIN mess_status m USING (mess_no)")
        inmates = cursor.fetchall()
        cursor.close()
        return render_template('index.html', inmates=inmates)
    except:
        return "Some error occurred!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)