from datetime import datetime

def check_date_format(date_str):
    formats_to_check = [
        '%Y-%m-%d',          # YYYY-MM-DD
        '%m/%d/%Y',          # MM/DD/YYYY
        '%d-%m-%Y',          # DD-MM-YYYY
        '%Y/%m/%d',          # YYYY/MM/DD
        '%d/%m/%Y',          # DD/MM/YYYY
        '%b %d %Y',          # Abbreviated month name, space, day, space, year (e.g., Sep 02 2023)
        # Add more formats as needed
    ]

    for date_format in formats_to_check:
        try:
            datetime.strptime(date_str, date_format)
            return date_format
        except ValueError:
            pass

    return None