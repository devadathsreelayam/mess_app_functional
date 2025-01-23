import pymysql
import random
from datetime import datetime, timedelta

# Database connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="mess"
)
cursor = conn.cursor()

# Step 1: Get the list of mess numbers from the inmates table
cursor.execute("SELECT mess_no FROM inmates")
inmates = cursor.fetchall()

# Step 2: Generate dates for the current month
today = datetime.today()
start_date = today.replace(day=1)  # First day of the month
end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))  # Last day of the month

current_date = start_date
dates = []
while current_date <= end_date:
    dates.append(current_date)
    current_date += timedelta(days=1)

# Step 3: Populate the mess_status table
insert_query = """
    INSERT INTO mess_status (mess_no, update_date, in_status)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE in_status = VALUES(in_status)
"""

# Generate and insert random "in" or "out" values
for inmate in inmates:
    mess_no = inmate[0]
    for date in dates:
        in_status = random.choice(["in", "out"])
        cursor.execute(insert_query, (mess_no, date.strftime('%Y-%m-%d'), in_status))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully!")
