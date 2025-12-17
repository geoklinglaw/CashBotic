import logging
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo


def import_token():
    load_dotenv()
    token = os.getenv("TOKEN")

    if not token:
        raise ValueError(
            "Bot token not found! Make sure it's defined in the .env file.")
    return token


def import_spreadsheetID():
    load_dotenv()
    token = os.getenv("SPREADSHEET_ID")
    if not token:
        raise ValueError(
            "Bot token not found! Make sure it's defined in the .env file.")
    return token


def find_month(date_str: str | None = None) -> str:
    """
    Return the month’s English name given a dd/MM/yyyy string.
    If no date provided, uses today.
    """
    date_str = date_str or find_date()
    logging.info(f"DATEE {date_str}")
    mm = date_str[5:7]
    return DATES[mm]


def find_date() -> str:
    """dd/MM/yyyy in Asia/Singapore (GMT+8)."""
    sg = ZoneInfo("Asia/Singapore")
    return datetime.now(tz=sg).strftime("%Y-%m-%d")


def escape_markdown_v2(text):
    escape_chars = '_[]()~`>#+-=|{}.!'
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


# format insights msg
def format_insights_message(insights: dict) -> str:
    def safe(val):
        return val if val not in ("", None) else "0"

    avg = insights["averages"]
    spend = insights["spend_types"]
    categories = insights["category_breakdown"]

    lines = []

    lines.append("📈 *This Month’s Insights*\n")

    lines.append("*Averages*")
    lines.append(f"• Weekday: {escape_markdown_v2(safe(avg['weekday']))}")
    lines.append(f"• Weekend: {escape_markdown_v2(safe(avg['weekend']))}")
    lines.append(
        f"• Difference: {escape_markdown_v2(safe(avg['percentage_diff']))}\n")

    lines.append("*Spend Types*")
    lines.append(
        f"• Essential: {escape_markdown_v2(safe(spend['essential']))}")
    lines.append(
        f"• Discretionary: {escape_markdown_v2(safe(spend['discretionary']))}")
    lines.append(
        f"• Recurring: {escape_markdown_v2(safe(spend['recurring']))}")
    lines.append(
        f"• One\\-off: {escape_markdown_v2(safe(spend['one_off']))}\n")

    lines.append("*Top Categories*")
    for k, v in categories.items():
        if safe(v) != "$0.00":
            lines.append(f"•{k}: {escape_markdown_v2(v)}")

    lines.append(f"\n\n*Total Spending*")
    lines.append(f"{escape_markdown_v2(safe(insights['total']))}")

    return "\n".join(lines)


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
CATEGORIES = ["Income", "Food", "Transport", "Education",
              "Shopping", "Gifts", "Lifestyle", "Travel", "Subscriptions"]
HEADERS = ["Date", "Product", "Price", "Category", "Spend Type"]
CATEGORY_TO_SPEND_TYPE_DEFAULT = {
    "Income": "Income",  # special case
    "Food": "Essential",
    "Transport": "Essential",
    "Education": "Essential",
    "Shopping": "Discretionary",
    "Gifts": "Discretionary",
    "Lifestyle": "Discretionary",
    "Travel": "One-off",
    "Subscriptions": "Recurring",
}
