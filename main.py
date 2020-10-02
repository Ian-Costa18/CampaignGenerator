""" Main File for Campaign Generator """

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1uEgXihcCi8Ixks3kb4q6nbzWy6rOcSq0JDD0eMn2cnA'
SAMPLE_RANGE_NAME = 'Form Responses 1!A2:E'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            for i in range(5):
                try:
                    print(f"{row[i]}", end=", ")
                except IndexError as err:
                    print(f"Nothing in column #{i}")
            print()



if __name__ == '__main__':
    main()




"""
import json
from google.oauth2 import service_account
import gspread
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    SECRETS_FILE = "campaign-generator-291301-900024a08528.json"
    SPREADSHEET = "testformspreadsheet"

    json_key = json.load(open(SECRETS_FILE))
    # Authenticate using the signed key
    credentials = service_account.Credentials.from_service_account_file(
        SECRETS_FILE, scopes=SCOPE)
    gc = gspread.authorize(credentials)
    workbook = gc.open(SPREADSHEET)
    print(workbook)
"""