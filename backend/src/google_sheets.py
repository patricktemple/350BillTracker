from __future__ import print_function

import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src import app, models, settings

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# TODO: Share this with TogglSync via a utils package?
def get_service():
    # TODO: This will need to refresh the creds every time after first expiration? Maybe?
    print(settings.GOOGLE_CREDENTIALS, flush=True)
    creds = Credentials.from_authorized_user_info(
        json.loads(settings.GOOGLE_CREDENTIALS), SCOPES
    )
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise ValueError(
                f"Creds were invalid but not refreshable: {GCAL_CREDENTIALS}"
            )

    service = build("sheets", "v4", credentials=creds)
    return service


def create_cell_data(raw_value, bold=False):
    return {
        "userEnteredValue": {"stringValue": str(raw_value)},
        "userEnteredFormat": {"textFormat": {"bold": bold}},
    }


def create_row_data(raw_values, bold=False):
    return {
        "values": [create_cell_data(value, bold=bold) for value in raw_values]
    }


def create_phone_bank_spreadsheet(bill_id):
    sponsorships = models.BillSponsorship.query.filter_by(
        bill_id=bill_id
    ).all()  # todo joinedload
    sponsorships = sorted(sponsorships, key=lambda s: s.legislator.name)

    rows = [
        create_row_data(["SPONSORS"], bold=True),
        create_row_data(
            ["Name", "Email", "District Phone", "Legislative Phone", "Notes"],
            bold=True,
        ),
    ]
    for sponsorship in sponsorships:
        legislator = sponsorship.legislator
        rows.append(
            create_row_data(
                [
                    legislator.name,
                    legislator.email,
                    legislator.district_phone,
                    legislator.legislative_phone,
                    legislator.notes,
                ]
            )
        )

    rows.append(create_row_data([]))
    rows.append(create_row_data(["NON-SPONSORS"]))  # or just empty row?

    sponsor_ids = [s.legislator_id for s in sponsorships]
    non_sponsors = (
        models.Legislator.query.filter(
            models.Legislator.id.not_in(sponsor_ids)
        )
        .order_by(models.Legislator.name)
        .all()
    )

    for legislator in non_sponsors:
        rows.append(
            [
                legislator.name,
                legislator.email,
                legislator.district_phone,
                legislator.legislative_phone,
                legislator.notes,
            ]
        )

    service = get_service()

    spreadsheet_data = {
        "properties": {"title": f"Phone bank for {sponsorships[0].bill.file}"},
        "sheets": [{"data": {"rowData": rows}}],
    }
    print(spreadsheet_data, flush=True)

    # TODO: Share this externally or with a specific person
    # right now it's only visible to the creator robot account
    return service.spreadsheets().create(body=spreadsheet_data).execute()

# {"properties": {"title": "Phone bank for Int 2317-2021"}, "sheets": [{"data": {"rowData": [{"values": [{"userEnteredValue": {"stringValue": "SPONSORS"}, "userEnteredFormat": 
