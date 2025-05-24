import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def clean_select_objects_split_str(input_str):
    cleaned_str = (input_str.strip('<').strip('>')
                          .replace("North Node", "Rahu")
                          .replace("South Node", "Ketu")
                          .replace("Pars Fortuna", "Fortuna"))
    return cleaned_str.split()

def utc_offset_str_to_float(utc_offset: str) -> float:
    hours, minutes = map(int, utc_offset.split(':'))
    return hours + minutes / 60.0 if utc_offset.startswith('+') else -1 * (abs(hours) + minutes / 60.0)

def pretty_data_table(named_tuple_data : list):
    from prettytable import PrettyTable
    table = PrettyTable()
    table.field_names = named_tuple_data[0]._fields 
    for data in named_tuple_data:
        table.add_row(data)
    return table

def dms_to_decdeg(dms_str: str):
    dms = dms_str.split(':')
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    return round(degrees + (minutes/60) + (seconds/3600), 4)

def dms_to_mins(dms_str: str):
    dms = dms_str.split(':')
    degrees = int(dms[0])
    minutes = int(dms[1])
    seconds = int(dms[2])
    total_minutes = degrees * 60 + minutes + seconds / 60
    return round(total_minutes, 2)  

def dms_difference(dms1_str: str, dms2_str: str):
    def dms_to_seconds(dms_str):
        dms = dms_str.split(':')
        degrees = int(dms[0])
        minutes = int(dms[1])
        seconds = int(dms[2])
        return degrees * 3600 + minutes * 60 + seconds

    def seconds_to_dms(seconds):
        degrees = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{int(degrees)}:{int(minutes)}:{int(seconds)}"

    dms1_seconds = dms_to_seconds(dms1_str)
    dms2_seconds = dms_to_seconds(dms2_str)
    diff_seconds = abs(dms1_seconds - dms2_seconds)
    return seconds_to_dms(diff_seconds)

def convert_years_ymdhm(years):
    months_per_year = 12
    days_per_month = 30
    hours_per_day = 24
    minutes_per_hour = 60

    whole_years = int(years)
    months = (years - whole_years) * months_per_year
    whole_months = int(months)
    days = (months - whole_months) * days_per_month
    whole_days = int(days)
    hours = (days - whole_days) * hours_per_day
    whole_hours = int(hours)
    minutes = (hours - whole_hours) * minutes_per_hour
    whole_minutes = int(minutes)

    return whole_years, whole_months, whole_days, whole_hours, whole_minutes

def compute_new_date(start_date : tuple, diff_value : float, direction: str):
    year, month, day, hour, minute = start_date
    years, months, days, hours, minutes = convert_years_ymdhm(diff_value)
    initial_date = datetime(year, month, day, hour, minute)
    time_difference = relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes)

    if direction == 'backward':
        new_date = initial_date - time_difference
    elif direction == 'forward':
        new_date = initial_date + time_difference
    else:
        raise ValueError("direction must be either 'backward' or 'forward'")

    return new_date

def get_utc_offset(timezone_loc: str, date: datetime):
    from pytz import timezone, FixedOffset, UnknownTimeZoneError

    try:
        tz = timezone(timezone_loc)
    except UnknownTimeZoneError:
        if ":" in timezone_loc:
            sign = 1 if timezone_loc[0] != "-" else -1
            hrs, mins = map(int, timezone_loc.strip("+").strip("-").split(":"))
            offset_minutes = sign * (hrs * 60 + mins)
            tz = FixedOffset(offset_minutes)
        else:
            raise

    localized_date = tz.localize(date)
    utc_offset_sec = localized_date.utcoffset().total_seconds()
    hours, remainder = divmod(abs(utc_offset_sec), 3600)
    minutes = remainder // 60
    sign = "+" if utc_offset_sec >= 0 else "-"
    utc_offset_str = f"{sign}{int(hours):02}:{int(minutes):02}"    
    utc_offset = timedelta(seconds=utc_offset_sec)

    return utc_offset_str, utc_offset

def calculate_pada_from_zodiac(sidereal_degree: float) -> int:
    
    nakshatra_starts = [
        0.0, 13.3333, 26.6667, 40.0, 53.3333, 66.6667, 80.0, 93.3333, 106.6667,
        120.0, 133.3333, 146.6667, 160.0, 173.3333, 186.6667, 200.0, 213.3333,
        226.6667, 240.0, 253.3333, 266.6667, 280.0, 293.3333, 306.6667, 320.0,
        333.3333, 346.6667
    ]
    nakshatra_span = 13.3333
    pada_span = nakshatra_span / 4  # 3.3333°

    for start in nakshatra_starts:
        end = start + nakshatra_span
        if start <= sidereal_degree < end:
            degree_within_nakshatra = sidereal_degree - start
            return int(degree_within_nakshatra / pada_span) + 1

    return 0

