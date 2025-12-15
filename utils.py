import logging
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

def import_token():
    load_dotenv()
    token = os.getenv("TOKEN")

    if not token:
        raise ValueError("Bot token not found! Make sure it's defined in the .env file.")
    return token

def import_spreadsheetID():
    load_dotenv()
    token = os.getenv("SPREADSHEET_ID")
    if not token:
        raise ValueError("Bot token not found! Make sure it's defined in the .env file.")
    return token


def find_month():
    return find_date().month

def find_date():
    return datetime.now(tz=ZoneInfo("Asia/Singapore"))
    
def escape_markdown_v2(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def chunk_list(lst, n):
    """Chunk a list into sublists of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

# format date from CALENDAR;DAY;2025;4;10 to 10/04/25
def format_calendar_date(raw_date):
    try:
        _, _, year, month, day = raw_date.split(';')
        formatted_date = f"{int(day):02d}/{int(month):02d}/{str(year)[-2:]}"
        return formatted_date
    except Exception as e:
        print(f"Error formatting date: {e}")
        return raw_date

def current_date_str() -> str:
    """dd/MM/yyyy in Asia/Singapore (GMT+8)."""
    sg = ZoneInfo("Asia/Singapore")
    return datetime.now(tz=sg).strftime("%d/%m/%Y")

def find_month_name(date_str: str | None = None) -> str:
    """
    Return the month’s English name given a dd/MM/yyyy string.
    If no date provided, uses today.
    """
    date_str = date_str or current_date_str()
    mm = date_str[3:5]
    return DATES[mm]


DATES = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

# STANDARD KEYBOARDS
KEYBOARD_CATEGORIES = ["Income", "Food", "Transport", "Education", "Entertainment", "Wants", "Gifts", "Sustenance",]
HEADERS = ["Date", "Product", "Price", "Category", "Claimable"]
