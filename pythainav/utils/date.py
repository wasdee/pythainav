import datetime

import dateparser


def date_range(start_date, end_date):
    return [
        start_date + datetime.timedelta(days=x)
        for x in range((end_date - start_date).days + 1)
    ]


def convert_buddhist_to_gregorian(input_date):
    if isinstance(input_date, str):
        input_date = dateparser.parse(input_date)
    year = input_date.year - 543
    input_date = input_date.replace(year=year)
    return input_date
