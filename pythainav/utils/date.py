import datetime

def date_range(start_date, end_date):
    return [start_date + datetime.timedelta(days=x) for x in range((end_date-start_date).days+1)]