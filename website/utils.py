import calendar
import datetime


def get_first_and_last_dates(month: str | int, year: int) -> tuple[datetime.date, datetime.date]:
    """
    Function to get the first date and last dates of a month from given month and year
    :param month: Name of month (str)
    :param year: Year (int)
    :return: First and last dates of the month
    """
    # Convert the month name to a number (1-12)
    if type(month) == str:
        month_number = list(calendar.month_name).index(month)
    else:
        month_number = month

    if month_number == 0:
        raise ValueError("Invalid month name")

    # Get the first date of the month
    first_date = datetime.datetime(year, month_number, 1).date()

    # Get the last day of the month
    last_day = calendar.monthrange(year, month_number)[1]
    last_date = datetime.datetime(year, month_number, last_day).date()

    return first_date, last_date