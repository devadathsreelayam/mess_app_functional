import pymysql
import pymysql.cursors

def __get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='mess'
    )


def view_all_inmates():
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM inmates')
        result = cursor.fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        return result
    except Exception as e:
        return None
    

def get_inmate(mess_no):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM inmates WHERE mess_no = %s', (mess_no, ))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()

        return result
    except Exception:
        return None


def update_inmate(mess_no, inmate_name, department, is_ablc):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            'UPDATE inmates SET inmate_name = %s, department = %s, is_ablc = %s WHERE mess_no = %s',
            (inmate_name, department, int(bool(is_ablc)), mess_no))
        connection.commit()
        cursor.close()
        connection.close()

        return 1

    except Exception:
        return None


def delete_inmate(mess_no):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute('DELETE FROM mess_status WHERE mess_no = %s', (mess_no,))  # Delete records from mess status
        cursor.execute('DELETE FROM mess_logs WHERE mess_no = %s', (mess_no,))  # Delete records from meal logs
        cursor.execute('DELETE FROM guest_logs WHERE mess_no = %s', (mess_no,))  # Delete records from guest logs
        cursor.execute('DELETE FROM inmates WHERE mess_no = %s', (mess_no,))  # Finally delete inmate from inmates table
        connection.commit()

        cursor.close()
        connection.close()

        return True  # Successfully deleted

    except Exception as e:
        print(f"Error during deletion: {e}")  # Log the error for debugging
        return None


def get_today_count():
    try:
        connection = __get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT COUNT(*) FROM inmates i
            JOIN mess_status ms
            USING (mess_no)
            WHERE ms.in_status = 'in' AND ms.update_date = CURDATE();"""
        )

        count = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        connection.close()

        if count:
            return count
        else:
            return "Error"

    except Exception as e:
        print(f"Error while taking count: {e}")  # Log the error for debugging
        return None