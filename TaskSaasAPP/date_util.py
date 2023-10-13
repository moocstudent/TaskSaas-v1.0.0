import calendar
import datetime


def get_last_week_since_today():
    seven_day = datetime.timedelta(days=6)
    return (datetime.datetime.now()-seven_day).strftime('%Y-%m-%d')

def get_month():
    return datetime.datetime.now().strftime('%m')

def get_today():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_today_until_second():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_year():
    return datetime.datetime.now().strftime('%Y')


def format_date(date,format):
    if format:
        return date.strftime(format)
    return date.strftime('%Y-%m-%d')
def get_every_day(day_trigger,day0,format):
    end_date = None
    begin_date = datetime.datetime.now()
    if day_trigger == 'day1':
        end_date = begin_date
    elif day_trigger == 'day7':
        end_date = begin_date-datetime.timedelta(days=6)
    elif day_trigger == 'day30':
        month_days = calendar.monthrange(begin_date.year, begin_date.month)[1]
        print(month_days)
        end_date = datetime.datetime(begin_date.year,begin_date.month,1)
        begin_date = datetime.datetime(begin_date.year,begin_date.month,month_days)
    elif day_trigger == 'day0':
        # begin_date
        end_date = day0-datetime.timedelta(days=1)
    else:
        return []
    print(end_date)
    every_days_date = [begin_date - datetime.timedelta(days=x) for x in range((begin_date - end_date).days + 1)]
    if format:
        format_every_days = []
        for d in every_days_date:
            format_every_days.append(format_date(d,format))
        return format_every_days
    return every_days_date

# print(get_every_day('day0','2023-01-01'))
