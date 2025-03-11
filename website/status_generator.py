import pymysql
import random
from datetime import datetime, timedelta

def generate_random_mess_in_status(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="mess_app_db"
    )
    cursor = conn.cursor()

    # Step 1: Get the list of mess numbers from the inmates table
    cursor.execute("SELECT inmate_id FROM inmate")
    inmates = cursor.fetchall()

    current_date = start_date
    dates = []
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    # Step 3: Populate the mess_status table
    insert_query = """
        INSERT INTO mess_status (inmate_id, update_date, in_status, last_edit, edited_by)
        VALUES (%s, %s, %s, %s, %s)
    """

    # Generate and insert random "in" or "out" values
    for inmate in inmates:
        mess_no = inmate[0]
        for date in dates:
            in_status = random.choice([True, False])
            cursor.execute(insert_query, (mess_no, date.strftime('%Y-%m-%d'), in_status, datetime.now(), 1))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted successfully!")


if __name__ == '__main__':
    generate_random_mess_in_status('2025-01-01', '2025-01-31')
