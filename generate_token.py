"""
IMPORTANT: 
run python generate_token.py if error is the following
invalid_grant: Token has been expired or revoked.',
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

scopes = ['https://www.googleapis.com/auth/spreadsheets']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)

creds = flow.run_local_server(port=0)
with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)

print("Credentials are saved for future use.")
