""" Main File for Campaign Generator """

import os
import pickle  # Rick
from time import sleep
from shutil import rmtree

import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from imgur_downloader.imgurdownloader import ImgurException

from candidateprocessor import process_candidate, send_error_email


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

def cleanup(current_candidate):

    CWD = os.path.dirname(__file__)
    output_directory = os.path.join(CWD, "output")
    output_files = os.listdir(output_directory)
    for file in output_files:
        try:
            if "Generated Campaign" in file:
                os.remove(os.path.join(output_directory, file))
            elif "zip" not in file:
                os.remove(os.path.join(output_directory, file))
        except Exception as err:
            print(f"{file} could not be deleted :(")
            continue
    main_files = os.listdir(CWD)
    for file in main_files:
        try:
            if current_candidate['name'] in file:
                os.remove(os.path.join(CWD, file))
            elif "temp" in file.lower():
                os.remove(os.path.join(CWD, file))
        except Exception as err:
            print(f"{file} could not be deleted :(")
            continue


def main():
    """ Main function for Campaign Generator """

    while True:

        unprocessed_candidates = get_spread()

        if not unprocessed_candidates:
            print('No new candidates to process')
            sleep(5)
            continue
        print("Found new candidates")
        for current_candidate in unprocessed_candidates:
            # Cleanup temporary files from previous candidates before doing anything
            cleanup(current_candidate)

            print(f"Processing canidate: {current_candidate['name']}")
            try:
                process_candidate(current_candidate, send_to_email=True)
                # Cleanup temporary files from the current candidate
                cleanup(current_candidate)
            except (KeyboardInterrupt, SystemExit):
                print("Program interrupted")
                raise
            except ImgurException as err:
                print("Error getting Imgur link, send error email...")
                error_message = ("The campaign generator failed to get your image from Imgur, "
                                 "please make sure you are using the direct link to the image (i.imgur.com)"
                                 "\nResubmit your campaign here: https://forms.gle/mAwfNwK9SSLR1Riy9")
                send_error_email(current_candidate["email"],
                                 "Campaign Generator Failed",
                                 error_message)
                continue
            except Exception as err:
                print(err)
                print("Unknown exception occurred, sending generic failure email")
                error_message = ("The campaign generator failed to generate your campaign, "
                                 "please resubmit your campaign here: https://forms.gle/mAwfNwK9SSLR1Riy9"
                                 "\nIf the issue still occurs please reply to this email with the exception below:"
                                f"\"\n{err}\""
                )
                send_error_email(current_candidate["email"],
                                 "Campaign Generator Failed",
                                 error_message)
                continue



if __name__ == '__main__':
    main()
