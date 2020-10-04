""" Main File for Campaign Generator """

import os
import pickle  # Rick
from time import sleep

import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from candidateprocessor import process_candidate


def get_spread():
    """ Get's the contents of the Campaign Generator Spreadsheet
    Outputs a list of candidates not seen by the program before"""

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive']

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

    # Initialize gspread client with credentials then open spreadsheet
    gc = gspread.Client(creds)
    sheet = gc.open("Campaign Generator Spreadsheet")
    worksheet = sheet.sheet1
    # Get spreadsheet values
    values = sheet.sheet1.get_all_values()
    values.remove(values[0]) # Remove headers

    # Find unprocessed rows
    unprocessed = []
    for row in values:
        if row[10].lower() == "yes":
            continue
        unprocessed.append(row)
        index = values.index(row)
        worksheet.update(f"K{index+2}", "Yes")

    candidate_list = []
    for row in unprocessed:
        candidate_list.append({
            "timestamp": row[0],
            "email": row[1],
            "name": row[2],
            "position": row[3],
            "district": row[4],
            "party": row[5],
            "issues": [row[6], row[7], row[8]],
            "image": row[9]
        })

    return candidate_list


def main():
    """ Main function for Campaign Generator """

    thread = None
    while True:

        unprocessed_candidates = get_spread()

        if not unprocessed_candidates:
            print('No new candidates to process')
            sleep(5)
            continue
        print("Found new candidates")
        process_candidate(unprocessed_candidates, send_to_email=True)





if __name__ == '__main__':
    main()
