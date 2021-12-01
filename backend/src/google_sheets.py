from __future__ import print_function

import json

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import selectinload
from werkzeug import exceptions

from src import app, models, settings, twitter

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

COLUMN_TITLES = [
    "",
    "Name",
    "Email",
    "Party",
    "Borough",
    "District Phone",
    "Legislative Phone",
    "Twitter",
    "Twitter search\nNote: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this.",
    "Staffers",
    "Notes",
]

BOROUGH_SORT_TABLE = {
    "Brooklyn": 0,
    "Manhattan": 1,
    "Manhattan and Bronx": 2,
    "Queens": 3,
    "Bronx": 4,
    "Staten Island": 5,
}
BOROUGH_DEFAULT_SORT = 6

# Width in pixels for each column. We can't dynamically set it to match the,
# contents via the API, so instead we just hardcode them as best we can.
COLUMN_WIDTHS = [
    150,
    150,
    200,
    50,
    100,
    100,
    150,
    200,
    250,
    250,
]


class Cell:
    value = None  # str
    link_url = None  # str
    bold = False

    def __init__(self, value, *, link_url=None, bold=False):
        self.value = value
        self.link_url = link_url
        self.bold = bold


def _get_google_credentials():
    return Credentials.from_service_account_info(
        json.loads(settings.GOOGLE_CREDENTIALS)
    )


def _get_sheets_service(credentials):
    return build("sheets", "v4", credentials=credentials)


def _get_drive_service(credentials):
    return build("drive", "v3", credentials=credentials)


def _create_cell_data(cell):
    text_format_runs = None
    if cell.link_url:
        text_format_runs = [
            {"startIndex": 0, "format": {"link": {"uri": cell.link_url}}}
        ]
    return {
        "textFormatRuns": text_format_runs,
        "userEnteredValue": {"stringValue": str(cell.value)},
        "userEnteredFormat": {
            "wrapStrategy": "WRAP",
            "textFormat": {"bold": cell.bold},
        },
    }


def _create_row_data(cells):
    return {"values": [_create_cell_data(cell) for cell in cells]}


def _create_legislator_row(legislator, bill, is_lead_sponsor=False):
    staffer_strings = [s.display_string for s in legislator.staffers]
    staffer_text = "\n\n".join(staffer_strings)

    twitter_search_url = twitter.get_bill_twitter_search_url(bill, legislator)

    cells = [
        Cell(""),
        Cell(f"{legislator.name}{' (lead)' if is_lead_sponsor else ''}"),
        Cell(legislator.email),
        Cell(legislator.party),
        Cell(legislator.borough),
        Cell(legislator.district_phone),
        Cell(legislator.legislative_phone),
        Cell(
            legislator.display_twitter or "", link_url=legislator.twitter_url
        ),
        Cell(
            "Relevant tweets" if twitter_search_url else "",
            link_url=twitter_search_url,
        ),
        Cell(staffer_text),
        Cell(legislator.notes or ""),
    ]
    return _create_row_data(cells)


def _create_title_row_data(raw_values):
    cells = [Cell(value, bold=True) for value in raw_values]
    return _create_row_data(cells)


def _create_phone_bank_spreadsheet_data(bill, sponsorships, non_sponsors):
    """Generates the full body payload that the Sheets API requires for a
    phone bank spreadsheet."""
    rows = [
        _create_title_row_data(
            COLUMN_TITLES,
        ),
        _create_title_row_data(["NON-SPONSORS"]),
    ]
    for legislator in non_sponsors:
        rows.append(_create_legislator_row(legislator, bill))

    rows.append(_create_title_row_data([]))
    rows.append(_create_title_row_data(["SPONSORS"]))

    for sponsorship in sponsorships:
        rows.append(
            _create_legislator_row(
                sponsorship.legislator, bill, sponsorship.sponsor_sequence == 0
            )
        )

    column_metadata = [{"pixelSize": size} for size in COLUMN_WIDTHS]
    return {
        "properties": {"title": f"Phone bank for {bill.file}"},
        "sheets": [
            {
                "properties": {"gridProperties": {"frozenRowCount": 1}},
                "data": {"rowData": rows, "columnMetadata": column_metadata},
            }
        ],
    }


def get_sort_key(legislator):
    sort_key = BOROUGH_SORT_TABLE.get(legislator.borough, BOROUGH_DEFAULT_SORT)
    return (sort_key, legislator.name)


def create_phone_bank_spreadsheet(bill_id):
    """Creates a spreadsheet that's a template to run a phone bank
    for a specific bill, based on its current sponsors. The sheet will be
    owned by a robot Google account and will be made publicly editable by
    anyone with the link."""
    bill = (
        models.Bill.query.filter_by(id=bill_id)
        .options(
            selectinload(models.Bill.sponsorships),
            selectinload("sponsorships.legislator.staffers"),
        )
        .one()
    )

    sponsorships = bill.sponsorships
    sponsorships = sorted(
        sponsorships, key=lambda s: get_sort_key(s.legislator)
    )

    sponsor_ids = [s.legislator_id for s in sponsorships]
    non_sponsors = models.Legislator.query.filter(
        models.Legislator.id.not_in(sponsor_ids)
    ).all()
    non_sponsors = sorted(non_sponsors, key=get_sort_key)

    spreadsheet_data = _create_phone_bank_spreadsheet_data(
        bill, sponsorships, non_sponsors
    )

    google_credentials = _get_google_credentials()
    sheets_service = _get_sheets_service(google_credentials)

    spreadsheet_result = (
        sheets_service.spreadsheets().create(body=spreadsheet_data).execute()
    )

    # That sheet is initially only accessible to our robot account, so make it public.
    drive_service = _get_drive_service(google_credentials)
    user_permission = {
        "type": "anyone",
        "role": "writer",
    }
    drive_service.permissions().create(
        fileId=spreadsheet_result["spreadsheetId"],
        body=user_permission,
        fields="id",
    ).execute()

    return spreadsheet_result


def extract_data_from_previous_power_hour(spreadsheet_id):
    google_credentials = _get_google_credentials()
    sheets_service = _get_sheets_service(google_credentials)

    # TODO: Use a field mask instead of includeGridData=true to return less data
    spreadsheet = (
        sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=True).execute()
    )
    row_data = spreadsheet['sheets'][0]['data'][0]['rowData']
    def get_data(column):
        if 'effectiveValue' in column:
            return column['effectiveValue']['stringValue'] # TODO research best way for all this
        return ""
    def get_columns(row):
        if 'values' in row:
            return [get_data(column) for column in row['values']]
        return []
    raw_cell_data = [get_columns(row) for row in row_data]

    title_row = raw_cell_data[0]
    data_rows = raw_cell_data[1:]

    # Data structure I want:
    # { legislator_name: {
    #       extra_column_title_1: extra_column_value,
    #       extra_column_title_2: extra_column_value
    # }
    # }

    # then, when generating, for each legislator I can add the value for each extra column name

    column_title_set = set(COLUMN_TITLES)
    extra_column_titles = [] # tuple: (id, text)
    name_column_index = None
    for i, title in enumerate(title_row):
        if title not in column_title_set:
            extra_column_titles.append((i, title))
        elif title == "Name":
            name_column_index = i

    data = {}
    for row in data_rows:
        if name_column_index < len(row) and (name := row[name_column_index]) is not None:
            # Ignore empty rows, they might just be for space
            legislator = {}
            for index, extra_column_title in extra_column_titles:
                if index < len(row):
                    legislator[extra_column_title] = row[index]
            data[name] = legislator
    
    return ([title[1] for title in extra_column_titles], data)


    # Now, for each title row, look for:
    # Name
    # Any other rows that are auto-generated
    # Any other rows we don't know about
    # Build a map of the values in the last one
    # Then make a representation of this that can be inserted into future spreadsheets