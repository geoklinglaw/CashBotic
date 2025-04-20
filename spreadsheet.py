import os
import base64
import pickle
import logging
from datetime import date
from typing import List
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from expenditure import Expenditure
from utils import find_date, find_month, current_date_str, find_month_name, import_spreadsheetID

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

if not os.path.exists("token.pickle") and os.path.exists("token.b64.txt"):
    logging.info("Decoding token.pickle from token.b64.txt...")
    with open("token.b64.txt", "rb") as f_in:
        encoded = f_in.read()
    with open("token.pickle", "wb") as f_out:
        f_out.write(base64.b64decode(encoded))
    logging.info("token.pickle created successfully.")

with open("token.pickle", "rb") as token:
    creds = pickle.load(token)

service = build("sheets", "v4", credentials=creds, cache_discovery=False)
SPREADSHEET_ID = import_spreadsheetID()         
MONTH_TAB      = find_month_name()   
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
        month_tab   = _ensure_month_tab()                    # ← today's month
        range_name  = f"'{month_tab}'!A:C"
        values = [[expenditure.date, expenditure.product, expenditure.amount]]  
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
Date/Time Handlers
'''

def add_headers(
    service, spreadsheet_id: str, sheet_id: int, headers: List[str]
) -> None:
    """
    ► Append a header row
    ► Centre‑align it
    """
    # 1) append the row
    body = {"values": [headers]}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_id}'!A1",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

    # 2) centre‑align the header we just wrote
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(headers),
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
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()


def ensure_date_break(service, spreadsheet_id: str, sheet_name: str, today: str | None = None) -> None:
    """
    Make sure the last written date is *today*; if not, insert two blank rows.
    """
    today = today or current_date_str()
    # Pull the last non‑empty cell in column A
    col_a = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A:A")
        .execute()
        .get("values", [])
    )
    last_row_idx = len(col_a)
    if last_row_idx <= 1:       # header only → nothing to check
        return

    prev_date = col_a[-1][0]    # last value in column A
    if prev_date != today:
        logging.info("Date break detected – inserting two rows …")
        requests = [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": _get_sheet_id(service, spreadsheet_id, sheet_name),
                        "dimension": "ROWS",
                        "startIndex": last_row_idx,
                        "endIndex": last_row_idx + 2,
                    },
                    "inheritFromBefore": False,
                }
            }
        ]
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()


'''
Sheet creation
'''
def create_month_tab(service, spreadsheet_id: str) -> int:
    """
    Create a *new worksheet* named for the current month,
    add headers, return the numeric sheetId.
    """
    title = find_month_name()
    requests = [{"addSheet": {"properties": {"title": title}}}]
    res = (
        service.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests})
        .execute()
    )
    sheet_id = res["replies"][0]["addSheet"]["properties"]["sheetId"]
    add_headers(
        service,
        spreadsheet_id,
        sheet_id,
        ["Date", "Product", "Price", "Category", "Claimable"],
    )
    logging.info(f"Created new tab «{title}» ({sheet_id})")
    return sheet_id

def _get_sheet_id(title: str) -> int:
    meta = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, includeGridData=False
    ).execute()
    for s in meta["sheets"]:
        if s["properties"]["title"] == title:
            return s["properties"]["sheetId"]
    raise KeyError(f"Tab “{title}” not found")

def _add_headers(sheet_id: int) -> None:
    """Write header row + centre it."""
    headers = ["Date", "Product", "Price", "Category", "Claimable"]

    # value write
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"A1:{chr(64+len(headers))}1",        # A1:E1
        valueInputOption="USER_ENTERED",
        body={"values": [headers]},
    ).execute()

    # format centre + bold
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
                            "endColumnIndex": len(headers),
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
    _add_headers(sheet_id)
    logging.info(f"Created tab «{title}» ({sheet_id})")


def _ensure_month_tab() -> str:
    """Return the current‑month tab name, creating it if missing."""
    title = find_month_name()
    if title not in _get_titles():
        _create_month_tab(title)
    return title