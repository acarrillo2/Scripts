import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, FR

def get_six_months_ago():
    return (datetime.now() - relativedelta(months=6))

def generate_t8_week_friday_strings():
    last_friday = datetime.now() + relativedelta(weekday=FR(-1))
    t8_fridays = [last_friday]
    for i in range(7):
        last_friday = last_friday - timedelta(days=7)
        t8_fridays.append(last_friday)
    return convert_date_list_to_strings(t8_fridays)

def generate_t6_month_end_date_strings():
    six_months_ago = get_six_months_ago()
    t6_month_end = []
    year = six_months_ago.year
    month = six_months_ago.month
    for i in range(6):
        month_end_day = calendar.monthrange(year, month)[1]
        month_end_date = datetime(year, month, month_end_day)
        last_fridayrelativedelta(day=31, weekday=FR(-1))
        t6_month_end.append(month_end_date)
        if month == 12:
            month = 1
            year += year
        else:
            month += 1
    return convert_date_list_to_strings(t6_month_end)
    
def convert_date_list_to_strings(date_list):
    date_list_str = []
    for timestamp in date_list:
        date_list_str.append(timestamp.strftime("%Y-%m-%d"))
    date_list_str.sort()
    return date_list_str
