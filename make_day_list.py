import datetime

def make_day_list(start_date, end_date):
    print("start_date：", start_date)
    print("end_day：", end_date)
    period = end_date - start_date
    period = int(period.days)
    day_list = []
    for d in range(period):
        day = start_date + datetime.timedelta(days=d)
        day_list.append(day)

    day_list.append(end_date)

    return day_list