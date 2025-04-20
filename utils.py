import logging
from dotenv import load_dotenv
import os
from datetime import date
import datetime

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
    return datetime.datetime.now()
    
def escape_markdown_v2(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def chunk_list(lst, n):
    """Chunk a list into sublists of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

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

KEYBOARD_CLAIMABLE = {
    "inline_keyboard": [
        [{"text": "can be claimed", "callback_data": 'claim_can claim'}],
        [{"text": "cannot be claimed", "callback_data": 'claim_cannot claim'}],
    ]
}

