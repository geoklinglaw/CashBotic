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
from utils import find_date, find_month, import_spreadsheetID, HEADERS

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


async def create_spreadsheet(service, month: str | None = None) -> str:
    try:
        month = month or find_month()
        spreadsheet = {"properties": {"title": month}}
        spreadsheet = (
            service.spreadsheets()
            .create(body=spreadsheet, fields=import_spreadsheetID())
            .execute()
        )
        print(f"Spreadsheet ID: {(spreadsheet.get(import_spreadsheetID()))}")
        return spreadsheet.get("spreadsheetId")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


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
