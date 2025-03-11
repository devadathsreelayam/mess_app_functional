import pandas as pd
import pymysql.cursors
import pymysql


def __get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='mess'
    )


def monthly_report(first_date, last_date):
    connection = __get_db_connection()

    # 1. Get the inmates who joined the mess on or before the month
    inmates_df = pd.read_sql_query(
        "SELECT mess_no, inmate_name, department, is_ablc FROM inmates WHERE join_date <= %s;",
        connection,
        params=[last_date]
    )

    # 2. Get the total inmate count of the month
    inmate_count = inmates_df.shape[0]

    # 3. Get total 'in' status count for the mess status within the month range
    mess_in_df = pd.read_sql_query(
        """
        SELECT mess_no, COUNT(in_status) AS mess_in_count
        FROM mess_status 
        WHERE in_status = 'in' AND update_date BETWEEN %s AND %s 
        GROUP BY mess_no;
        """,
        connection,
        params=[first_date, last_date]
    )

    total_mess_in_count = mess_in_df['mess_in_count'].sum()

    # 4. Get guest and sg count from guest_logs table
    guest_df = pd.read_sql_query(
        """
        SELECT mess_no, SUM(guest_count) AS guest_count, SUM(sg_count) AS sg_count 
        FROM guest_logs 
        WHERE log_date BETWEEN %s AND %s
        GROUP BY mess_no;
        """,
        connection,
        params=[first_date, last_date]
    )

    guest_df['guest_count'] = guest_df['guest_count'].astype(int)
    guest_df['sg_count'] = guest_df['sg_count'].astype(int)

    guest_count = guest_df['guest_count'].sum()
    sg_count = guest_df['sg_count'].sum()
    total_guest_count = guest_count + sg_count

    # 5. Get fixed and purchase expenses for the month
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
    cursor.close()

    # 6. Get guest charges from monthly_bill_info for the month and year
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        """
        SELECT guest_amount, opening_stock, closing_stock, vacated_amount_fixed, vacated_amount_daily
        FROM monthly_bill_info 
        WHERE month = MONTH(%s) AND year = (%s);
        """, (first_date, first_date)
    )

    monthly_info = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    # 1. Calculate guest charges
    # Guest charges = total guest count * guest fixed charge
    guest_charges = total_guest_count * monthly_info['guest_amount']

    # 2. Calculate net purchase amount
    # Net purchase = total purchase + opening stock - closing stock
    net_purchase = round(total_purchase + monthly_info['opening_stock'] - monthly_info['closing_stock'], 2)
    total_mess_in_expense = round((net_purchase - guest_charges - monthly_info['vacated_amount_daily']), 2)

    # 3. Total fixed amount calculation
    # Total fixed = fixed amount - vacated amount (fixed)
    net_fixed_expense = round(total_fixed - monthly_info['vacated_amount_fixed'], 2)

    per_day_expense = round((total_mess_in_expense / total_mess_in_count), 2)
    per_day_fixed = round((net_fixed_expense / inmate_count), 2)

    monthly_stat = {
        'net_purchase': net_purchase,
        'net_fixed': net_fixed_expense,
        'total_guest_count': guest_count,
        'total_sg_count': sg_count,
        'guest_fixed_amount': monthly_info['guest_amount'],
        'total_guest_charges': guest_charges,
        'inmate_count': inmate_count,
        'join_count': total_mess_in_count,
        'fixed_per_head': per_day_fixed,
        'expense_per_head': per_day_expense
    }

    return monthly_stat




# Example of how to call the function
guest = monthly_report('2025-01-01', '2025-01-31')
print(type(guest))
