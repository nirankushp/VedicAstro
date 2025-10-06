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

import calendar


def convert_years_ymdhm(years, start_date):
    """Convert fractional years to year, month, day, hour and minute components.

    Parameters
    ----------
    years : float
        Duration in years. Fractions are converted using actual calendar month
        lengths from ``start_date``.
    start_date : tuple
        Tuple of ``(year, month, day, hour, minute)`` representing the starting
        date used to resolve month lengths and leap years.

    Returns
    -------
    tuple
        ``(years, months, days, hours, minutes)`` suitable for building a
        ``relativedelta``.
    """

    year, month, day, hour, minute = start_date
    base_date = datetime(year, month, day, hour, minute)

    whole_years = int(years)
    date_after_years = base_date + relativedelta(years=whole_years)

    remaining_years = years - whole_years
    months_total = remaining_years * 12
    whole_months = int(months_total)
    date_after_months = date_after_years + relativedelta(months=whole_months)

    remaining_month_fraction = months_total - whole_months
    days_in_month = calendar.monthrange(date_after_months.year,
                                        date_after_months.month)[1]
    days_total = remaining_month_fraction * days_in_month
    whole_days = int(days_total)
    date_after_days = date_after_months + relativedelta(days=whole_days)

    remaining_day_fraction = days_total - whole_days
    hours_total = remaining_day_fraction * 24
    whole_hours = int(hours_total)
    date_after_hours = date_after_days + relativedelta(hours=whole_hours)

    remaining_hour_fraction = hours_total - whole_hours
    minutes_total = remaining_hour_fraction * 60
    whole_minutes = int(minutes_total)

    return whole_years, whole_months, whole_days, whole_hours, whole_minutes

def compute_new_date(start_date : tuple, diff_value : float, direction: str):
    year, month, day, hour, minute = start_date
    years, months, days, hours, minutes = convert_years_ymdhm(diff_value,
                                                              start_date)
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
        cleaned_loc = timezone_loc.strip()

        # Handle strings that include common prefixes such as ``UTC`` or ``GMT``
        for prefix in ("UTC", "GMT"):
            if cleaned_loc.upper().startswith(prefix):
                cleaned_loc = cleaned_loc[len(prefix):]
                break

        cleaned_loc = cleaned_loc.strip()

        if not cleaned_loc:
            tz = FixedOffset(0)
        else:
            if ":" in cleaned_loc:
                sign = 1 if cleaned_loc[0] != "-" else -1
                hrs, mins = map(int, cleaned_loc.strip("+").strip("-").split(":"))
            else:
                sign = 1
                offset_str = cleaned_loc
                if cleaned_loc[0] in "+-":
                    sign = 1 if cleaned_loc[0] == "+" else -1
                    offset_str = cleaned_loc[1:]

                if not offset_str.isdigit():
                    raise

                hrs = int(offset_str)
                mins = 0

            offset_minutes = sign * (hrs * 60 + mins)
            tz = FixedOffset(offset_minutes)

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

