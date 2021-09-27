from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src import app, models

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
SAMPLE_RANGE_NAME = "Class Data!A2:E"

TOKEN_FILE = "src/sheets/.token.json"


def create_cell_data(raw_value):
    return {"userEnteredValue": {"stringValue": str(raw_value)}}


def create_row_data(raw_values):
    return {"values": [create_cell_data(value) for value in raw_values]}


def create_sheet_data(raw_rows):
    return {"data": {"rowData": [create_row_data(row) for row in raw_rows]}}

def create_spreadsheet_data(title, raw_rows):
    return {
        "properties": {"title": title},
        "sheets": [create_sheet_data(raw_rows)],
    }

def create_sponsor_spreadsheet(bill_id):
  sponsorships = models.BillSponsorship.query.filter_by(bill_id=bill_id).all() # todo joinedload

  rows = [["Name", "Email", "District Phone", "Legislative Phone", "Notes"]]
  for sponsorship in sponsorships:
    legislator = sponsorship.legislator
    rows.append([legislator.name, legislator.email, legislator.district_phone, legislator.legislative_phone, legislator.notes])
  
  return create_spreadsheet_data(f"[TEST] Sponsors for {sponsorships[0].bill.file}", rows)


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "src/sheets/.credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)

    spreadsheet = create_sponsor_spreadsheet(67251)
    # Call the Sheets API
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=SAMPLE_RANGE_NAME).execute()

    print(sheet)


if __name__ == "__main__":
    main()
