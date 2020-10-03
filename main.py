""" Main File for Campaign Generator """

import pickle # Rick
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from signmaker import generate_sign
from imgur_downloader import ImgurDownloader
import os
from shutil import rmtree
from zipfile import ZipFile


def get_spread():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SPREADSHEET_ID = '1tcelDATAXNuReqC8zSxlcOKaruEGFaE96V5E7Q-XNwQ'
    RANGE_NAME = 'Form Responses 1!A2:J'

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
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values




def main():

    values = get_spread()

    if not values:
        print('No data found in spreadsheet')
        return

    data = []
    for row in values:
        data.append({
            "timestamp": row[0],
            "email": row[1],
            "name": row[2],
            "position": row[3],
            "district": row[4],
            "party": row[5],
            "issues": [row[6], row[7], row[8]],
            "image": row[9]
        })

    # Create the campaign sign
    current_canidate = data[0]
    use_local_image = False
    if use_local_image:
        canidate_image = "me2.jpg"
    else:
        ImgurDownloader(current_canidate["image"]).save_images("canidate_images")  # Download Imgur image/album
        canidate_image = f"canidate_images/{os.listdir('canidate_images')[0]}"  # Find the first image in the album

    generate_sign(current_canidate["name"], current_canidate["position"], current_canidate["district"],
                  current_canidate["party"], canidate_image, f"output/{current_canidate['name']} sign.png") # Generate the sign with the candidates data
    if not use_local_image:
        rmtree("canidate_images") # Delete the images folder

    # Create the campaign speech
    speech = f"""My Fellow Americans,

I stand before you today not to spew fancy political rhetoric or to talk about what could be better. I’m here today because you all are here. And you’re clearly fed up with politics. I’m here because our democracy isn’t working for all of us. You all know that this is the most important election of our lifetime. So I’m going to do something. This is why I, {current_canidate['name']}, am running to be the {current_canidate['position']} of {current_canidate['district']}.

You may think more divides us than unites us in this new era of politics. But I know we can all unite behind {current_canidate['issues'][0]}. Not only do our lives depend on making progress on {current_canidate['issues'][0]}, but so do the lives of our children.

However, putting our all towards {current_canidate['issues'][0]} won’t be enough to save our democracy. I know each and every single one you is struggling. That’s why I am also going to also focus on {current_canidate['issues'][1]} and {current_canidate['issues'][2]}. The elites in power feel too comfortable, so we need to shake things up. I am here today to listen to you, the American people, because I know you have been silenced for far too long. 

Vote {current_canidate['name']} for {current_canidate['position']} of {current_canidate['district']}!
"""
    print(speech)
    with open(f"output/{current_canidate['name']} speech.txt", "w") as file:
        file.write(speech)


    # Zip all files in output folder
    file_paths = os.listdir("output")
    with ZipFile('output/output.zip', 'w') as zip:
        # writing each file one by one
        os.chdir("output")
        for file in file_paths:
            zip.write(file)
            os.remove(file)
        zip.close()
        os.rename("output.zip", f"{current_canidate['name']}.zip")
        os.chdir("..")




if __name__ == '__main__':
    main()
