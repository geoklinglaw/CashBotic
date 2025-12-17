import os
import base64
import pickle
import logging
from datetime import date
from typing import List
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from expenditure import Expenditure
from dotenv import load_dotenv
from utils import find_date, find_month, import_spreadsheetID, HEADERS, CATEGORIES

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_google_credentials():
    """
    Load Google OAuth credentials from Railway environment variable.
    """
    b64 = os.environ.get("GOOGLE_TOKEN_PICKLE_B64")
    if not b64:
        raise RuntimeError("GOOGLE_TOKEN_PICKLE_B64 not set")

    logging.info("Loading Google credentials from environment variable")

    token_bytes = base64.b64decode(b64)
    creds = pickle.loads(token_bytes)

    return creds


creds = load_google_credentials()
service = build("sheets", "v4", credentials=creds, cache_discovery=False)
SPREADSHEET_ID = import_spreadsheetID()
MONTH_TAB = find_month()
titles = [
    s["properties"]["title"]
    for s in service.spreadsheets()
    .get(spreadsheetId=SPREADSHEET_ID, includeGridData=False)
    .execute()["sheets"]
]


def _get_titles() -> List[str]:
    """Return every worksheet title in the doc."""
    meta = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, includeGridData=False
    ).execute()
    return [s["properties"]["title"] for s in meta["sheets"]]


async def write(expenditure: Expenditure):
    try:
        month_tab = _ensure_month_tab()
        range_name = f"'{month_tab}'!A:E"
        values = [[expenditure.date, expenditure.product,
                   expenditure.amount, expenditure.category,
                   expenditure.spend_type]]
        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=import_spreadsheetID(),
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return result
    except Exception as e:
        logging.exception(f"Error writing to spreadsheet: {e}")
        return None

'''
Sheet creation
'''


def _add_headers(sheet_id: int, title: str) -> None:
    """Write header row + centre it."""
    logging.info("ADDING HEADERS")

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{title}!A1:{chr(64+len(HEADERS))}1",
        valueInputOption="USER_ENTERED",
        body={"values": [HEADERS]},
    ).execute()

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(HEADERS),
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "horizontalAlignment": "CENTER",
                                "textFormat": {"bold": True},
                            }
                        },
                        "fields": "userEnteredFormat(horizontalAlignment,textFormat)",
                    }
                }
            ]
        },
    ).execute()


def _create_month_tab(title: str) -> None:
    """Make a new tab for the month and seed headers."""
    res = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()
    sheet_id = res["replies"][0]["addSheet"]["properties"]["sheetId"]
    _add_headers(sheet_id, title)
    logging.info(f"Created tab «{title}» ({sheet_id})")


def _ensure_month_tab() -> str:
    """Return the current‑month tab name, creating it if missing."""
    title = find_month()
    if title not in _get_titles():
        _create_month_tab(title)
    return title


def get_insights() -> dict:
    monthly_results = fetch_monthly_insights(find_month())
    insights = parse_monthly_insights(monthly_results)
    logging.info("INSIGHTS 123")
    logging.info(insights)
    return insights


def fetch_monthly_insights(month_tab):
    ranges = [
        f"'{month_tab}'!G2:H11",   # category breakdown
        f"'{month_tab}'!J3",       # avg weekday
        f"'{month_tab}'!J6",       # avg weekend
        f"'{month_tab}'!J9",       # percentage diff
        f"'{month_tab}'!G14",      # recurring
        f"'{month_tab}'!G17",      # essential
        f"'{month_tab}'!G20",      # discretionary
        f"'{month_tab}'!G23",      # one-off
        f"'{month_tab}'!H25",      # total
    ]

    result = service.spreadsheets().values().batchGet(
        spreadsheetId=import_spreadsheetID(),
        ranges=ranges,
        valueRenderOption="FORMATTED_VALUE"
    ).execute()

    return result.get("valueRanges", [])


def parse_monthly_insights(value_ranges):
    # 1. Category breakdown
    rows = value_ranges[0].get("values", [])

    category_breakdown = {
        row[0]: row[1] if len(row) > 1 else "0"
        for row in rows
    }

    # 2. Averages
    avg_weekday = value_ranges[1].get("values", [["0"]])[0][0]
    avg_weekend = value_ranges[2].get("values", [["0"]])[0][0]
    pct_diff = value_ranges[3].get("values", [["N/A"]])[0][0]

    # 3. Spend types
    recurring = value_ranges[4].get("values", [["0"]])[0][0]
    essential = value_ranges[5].get("values", [["0"]])[0][0]
    discretionary = value_ranges[6].get("values", [["0"]])[0][0]
    one_off = value_ranges[7].get("values", [["0"]])[0][0]

    # 4. Total
    total = value_ranges[8].get("values", [["0"]])[0][0]
    
    return {
        "category_breakdown": category_breakdown,
        "averages": {
            "weekday": avg_weekday,
            "weekend": avg_weekend,
            "percentage_diff": pct_diff,
        },
        "spend_types": {
            "recurring": recurring,
            "essential": essential,
            "discretionary": discretionary,
            "one_off": one_off,
        },
        "total": total
    }
