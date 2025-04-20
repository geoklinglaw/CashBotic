# https://docs.google.com/spreadsheets/d/1pDeojCOeSrF4xPPduKtqDTDdNdDtQjz5FZfl8clY1jQ/edit?gid=0#gid=0

import pickle
import logging
from datetime import date
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from expenditure import Expenditure
from utils import find_date, find_month, import_spreadsheetID

"""
Run this file to generate a token.pickle after authenticating your google auth before running the telegram bot
"""

with open('token.pickle', 'rb') as token:
    creds = pickle.load(token)

service = build('sheets', 'v4', credentials=creds)

async def write(expenditure: Expenditure):
    try:
        range_name = 'Sheet1!A:C' # append data from next available row of A and B
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

async def create_spreadsheet():
  try:
    month = find_month()
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
  