import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import selectinload
from . import settings


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


@dataclass
class Cell:
    value: str = None
    link_url: str = None
    bold: bool = False


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


def create_row_data(cells):
    return {"values": [_create_cell_data(cell) for cell in cells]}


def create_bolded_row_data(raw_values):
    cells = [Cell(value, bold=True) for value in raw_values]
    return create_row_data(cells)


def create_spreadsheet(
    sheet_title: str,
    row_data: Dict,
    column_widths: List[int]
):
    """TODO"""

    column_metadata = [{"pixelSize": size} for size in column_widths]
    spreadsheet_data = {
        "properties": {"title": sheet_title},
        "sheets": [
            {
                "properties": {"gridProperties": {"frozenRowCount": 1}},
                "data": {"rowData": row_data, "columnMetadata": column_metadata},
            }
        ],
    }

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


def _get_raw_cell_data(spreadsheet):
    """Takes in a deeply nested Google Spreadsheet object and simplifies it into a
    2D array of cell data strings."""
    row_data = spreadsheet["sheets"][0]["data"][0]["rowData"]

    def get_data(cell):
        if "formattedValue" in cell:
            return cell["formattedValue"]
        return ""

    def get_columns(row):
        if "values" in row:
            return [get_data(cell) for cell in row["values"]]
        return []

    return [get_columns(row) for row in row_data]


def get_spreadsheet_cells(spreadsheet_id):
    """Looks up a sheet from google sheets service and returns the
    cell data as a 2D list of strings."""
    google_credentials = _get_google_credentials()
    sheets_service = _get_sheets_service(google_credentials)

    # TODO: Use a field mask instead of includeGridData=true to return less data
    spreadsheet = (
        sheets_service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id, includeGridData=True)
        .execute()
    )
    return _get_raw_cell_data(spreadsheet)