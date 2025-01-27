import calendar
from datetime import datetime
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


def get_all_expenses():
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            """SELECT e.*, u.user_name FROM expenses e
            JOIN users u ON e.added_by = u.userid
            ORDER BY e.bill_date DESC;"""
        )
        result = cursor.fetchall()
        connection.commit()
        cursor.close()
        connection.close()

        if result:
            for row in result:
                row['bill_date'] = datetime.strftime(row['bill_date'], '%d-%m-%Y')
                row['bill_amount'] = float(row['bill_amount'])
            return result
        else:
            return None

    except Exception as e:
        print(f"Error while fetching expenses: {e}")  # Log the error for debugging
        return None


def add_expense(expense_name, bill_date, shop_name, expense_type, expense_category, bill_amount):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO expenses (expense_name, bill_date, shop, type, category, bill_amount, added_by)
               VALUES (%s, %s, %s, %s, %s, %s, 'deva');""",
            (expense_name, bill_date, shop_name, expense_type, expense_category, bill_amount)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return 1

    except Exception as e:
        print(f"Error while fetching expenses: {e}")  # Log the error for debugging
        return None


def delete_expense(expense_id):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute('DELETE FROM expenses WHERE expense_id = %s', (expense_id,))  # Finally delete inmate from inmates table
        connection.commit()

        cursor.close()
        connection.close()

        return True  # Successfully deleted

    except Exception as e:
        print(f"Error during deletion: {e}")  # Log the error for debugging
        return None


def get_expense(expense_id):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute('SELECT * FROM expenses WHERE expense_id = %s', (expense_id, ))
        expense = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        if expense:
            return expense
        else:
            return None

    except Exception as e:
        print(f'Error occurred while fetching expense: {e}')
        return None


def update_expense(expense_id, expense_name, bill_date, shop_name, expense_type, expense_category, bill_amount):
    try:
        connection = __get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            """UPDATE expenses 
            SET expense_name = %s, bill_date = %s, shop = %s, type = %s, category = %s, bill_amount = %s 
            WHERE expense_id = %s""",
            (expense_name, bill_date, shop_name, expense_type, expense_category, bill_amount, expense_id)
        )
        connection.commit()

        cursor.close()
        connection.close()

        return True  # Successfully deleted

    except Exception as e:
        print(f"Error during deletion: {e}")  # Log the error for debugging
        return None


def get_first_and_last_dates(month_name, year):
    # Convert the month name to a number (1-12)
    month_number = list(calendar.month_name).index(month_name)

    if month_number == 0:
        raise ValueError("Invalid month name")

    # Get the first date of the month
    first_date = datetime(year, month_number, 1).date()

    # Get the last day of the month
    last_day = calendar.monthrange(year, month_number)[1]
    last_date = datetime(year, month_number, last_day).date()

    return first_date, last_date


def get_total_expenses_of_month(month, year):
    try:
        first_date, last_date = get_first_and_last_dates(month, year)

        print(first_date, last_date)

        connection = __get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT SUM(bill_amount) AS total_fixed
            FROM expenses
            WHERE type = 'fixed'
            AND bill_date BETWEEN %s AND %s;""", (first_date, last_date)
        )
        total_fixed = cursor.fetchone()[0]

        cursor.execute(
            """SELECT SUM(bill_amount) AS total_fixed
            FROM expenses
            WHERE type = 'purchase'
            AND bill_date BETWEEN %s AND %s;""", (first_date, last_date)
        )
        total_purchase = cursor.fetchone()[0]

        connection.commit()
        cursor.close()
        connection.close()

        return float(total_fixed), float(total_purchase)

    except Exception as e:
        print(f"Error during expense calculation: {e}")  # Log the error for debugging
        return None



if __name__ == '__main__':
    print(get_expense(3))
