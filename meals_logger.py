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

# Step 1: Get the list of mess numbers and dates where in_status = "in"
select_query = """
    SELECT mess_no, update_date 
    FROM mess_status 
    WHERE in_status = 'in'
"""
cursor.execute(select_query)
valid_entries = cursor.fetchall()

# Step 2: Generate random meal statuses (e.g., "yes" or "no" for breakfast, lunch, dinner)
insert_query = """
    INSERT INTO mess_logs (mess_no, log_date, breakfast, lunch, dinner)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        breakfast = VALUES(breakfast), 
        lunch = VALUES(lunch), 
        dinner = VALUES(dinner)
"""

# Loop through the valid entries and populate the meals table
for entry in valid_entries:
    mess_no = entry[0]
    log_date = entry[1]
    breakfast = random.choice([1, 0])
    lunch = random.choice([1, 0])
    dinner = random.choice([1, 0])

    # Insert the meal data into the meals table
    cursor.execute(insert_query, (mess_no, log_date, breakfast, lunch, dinner))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Meals data inserted successfully!")
