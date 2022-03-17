import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import selectinload

from . import settings, twitter
from .bill.models import AssemblyBill, Bill, CityBill, SenateBill, StateBill
from .google_sheets import (
    Cell,
    create_bolded_row_data,
    create_row_data,
    create_spreadsheet,
    get_spreadsheet_cells,
)
from .models import UUID
from .person.models import (
    AssemblyMember,
    CouncilMember,
    OfficeContact,
    Person,
    Senator,
)
from .sponsorship.models import (
    AssemblySponsorship,
    CitySponsorship,
    SenateSponsorship,
)

CITY_COLUMN_TITLES = [
    "",
    "Name",
    "Email",
    "Party",
    "Borough",
    "District Phone",
    "Legislative Phone",
    "Twitter",
    "Committees",
    "Staffers",
    "Twitter search\nNote: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this.",
]
CITY_COLUMN_TITLE_SET = set(CITY_COLUMN_TITLES)

STATE_COLUMN_TITLES = [
    "",
    "Name",
    "Email",
    "Party",
    "District",
    "District Contact",
    "Albany Contact",
    "Twitter",
    # "Committees",
    "Staffers",
    # "Twitter search\nNote: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this.",
]
CITY_COLUMN_TITLES = [
    "",
    "Name",
    "Email",
    "Party",
    "Borough",
    "District Phone",
    "Legislative Phone",
    "Twitter",
    "Committees",
    "Staffers",
    "Twitter search\nNote: Due to a Twitter bug, the Twitter search sometimes displays 0 results even when there should be should be matching tweets. Refreshing the Twitter page often fixes this.",
]

BOROUGH_SORT_TABLE = {
    "Brooklyn": 0,
    "Manhattan": 1,
    "Manhattan and Bronx": 2,
    "Queens": 3,
    "Bronx": 4,
    "Staten Island": 5,
}

# Width in pixels for each column. We can't dynamically set it to match the,
# contents via the API, so instead we just hardcode them as best we can.
CITY_COLUMN_WIDTHS = [150, 150, 200, 50, 100, 100, 150, 200, 250, 250, 250]


@dataclass
class PowerHourImportData:
    """Data about a previous power hour that will be copied into a new sheet."""

    extra_column_titles: List[str]
    column_data_by_legislator_id: Dict[id, Dict[str, str]]
    import_messages: List[str]


def _get_staffer_display_string(staffer: Person):
    contact_methods = [c.phone for c in staffer.office_contacts] + [
        staffer.email,
        staffer.display_twitter,
    ]
    contact_methods = [c for c in contact_methods if c]
    contact_string = ", ".join(contact_methods)
    if not contact_string:
        contact_string = "No contact info"
    title_string = f"{staffer.title} - " if staffer.title else ""
    return f"{title_string}{staffer.name} ({contact_string})"


def _get_imported_data_cells(person, import_data):
    cells = []
    legislator_data = import_data.column_data_by_legislator_id.get(person.id)
    if legislator_data is not None:
        for extra_column in import_data.extra_column_titles:
            text = legislator_data.get(extra_column, "")
            cells.append(Cell(text))
    else:
        logging.warning(f"No data for {person.name} in import data")
    return cells


def _create_council_member_row(
    council_member: CouncilMember,
    bill: Bill,
    import_data: Optional[PowerHourImportData],
    is_lead_sponsor: bool = False,
):
    staffer_strings = [
        _get_staffer_display_string(s)
        for s in council_member.person.staffer_persons
    ]
    staffer_text = "\n\n".join(staffer_strings)

    twitter_search_url = twitter.get_bill_twitter_search_url(
        bill, council_member.person
    )

    legislative_phone = ", ".join(
        (
            c.phone
            for c in council_member.person.office_contacts
            if c.phone
            and c.type == OfficeContact.OfficeContactType.CENTRAL_OFFICE
        )
    )
    district_phone = ", ".join(
        (
            c.phone
            for c in council_member.person.office_contacts
            if c.phone
            and c.type == OfficeContact.OfficeContactType.DISTRICT_OFFICE
        )
    )
    committees = "\n".join(
        sorted(
            [
                f"{m.committee.name}{' (chair)' if m.is_chair else ''}"
                for m in council_member.committee_memberships
            ]
        )
    )
    cells = [
        Cell(""),
        Cell(
            _get_sponsor_name_text(council_member.person.name, is_lead_sponsor)
        ),
        Cell(council_member.person.email),
        Cell(council_member.person.party),
        Cell(council_member.borough),
        Cell(district_phone),
        Cell(legislative_phone),
        Cell(
            council_member.person.display_twitter or "",
            link_url=council_member.person.twitter_url,
        ),
        Cell(committees),
        Cell(staffer_text),
        Cell(
            "Relevant tweets" if twitter_search_url else "",
            link_url=twitter_search_url,
        ),
    ]
    if import_data:
        cells.extend(
            _get_imported_data_cells(council_member.person, import_data)
        )

    return create_row_data(cells)


# TODO: Make generic to be all state reps
# Can I dedupe this more?
def _create_state_representative_row(
    representative: Person,
    bill: Bill,
    import_data: Optional[PowerHourImportData],
    is_lead_sponsor: bool = False,
):
    staffer_strings = [
        _get_staffer_display_string(s) for s in representative.staffer_persons
    ]
    staffer_text = "\n\n".join(staffer_strings)

    twitter_search_url = twitter.get_bill_twitter_search_url(
        bill, representative
    )

    # TODO: Improve contact info
    legislative_phone = ", ".join(
        (
            c.phone
            for c in representative.office_contacts
            if c.phone
            and c.type == OfficeContact.OfficeContactType.CENTRAL_OFFICE
        )
    )
    district_phone = ", ".join(
        (
            c.phone
            for c in representative.office_contacts
            if c.phone
            and c.type == OfficeContact.OfficeContactType.DISTRICT_OFFICE
        )
    )

    cells = [
        Cell(""),
        Cell(_get_sponsor_name_text(representative.name, is_lead_sponsor)),
        Cell(representative.email),
        Cell(representative.party),
        Cell(district_phone),
        Cell(legislative_phone),
        Cell(
            representative.display_twitter or "",
            link_url=representative.twitter_url,
        ),
        Cell(staffer_text),
        Cell(
            "Relevant tweets" if twitter_search_url else "",
            link_url=twitter_search_url,
        ),
    ]
    if import_data:
        cells.append(_get_imported_data_cells(representative, import_data))

    return create_row_data(cells)


def _create_city_power_hour_row_data(
    bill: Bill,
    sponsorships: List[CitySponsorship],
    non_sponsors: List[CouncilMember],
    import_data: Optional[PowerHourImportData],
):
    """Generates the full body payload that the Sheets API requires for a
    phone bank spreadsheet."""

    extra_titles = import_data.extra_column_titles if import_data else []
    rows = [
        create_bolded_row_data(
            CITY_COLUMN_TITLES + extra_titles,
        ),
        create_bolded_row_data(["NON-SPONSORS"]),
    ]
    for non_sponsor in non_sponsors:
        rows.append(_create_council_member_row(non_sponsor, bill, import_data))

    rows.append(create_row_data([]))
    rows.append(create_bolded_row_data(["SPONSORS"]))

    for sponsorship in sponsorships:
        rows.append(
            _create_council_member_row(
                sponsorship.council_member,
                bill,
                import_data,
                sponsorship.sponsor_sequence == 0,
            )
        )

    return rows


# TODO: Dedupe this with above!
def _create_state_power_hour_row_data(
    bill: Bill,
    sponsorships: List[SenateSponsorship],
    non_sponsors: List[Senator],
    import_data: Optional[PowerHourImportData],
):
    """Generates the full body payload that the Sheets API requires for a
    phone bank spreadsheet."""

    extra_titles = import_data.extra_column_titles if import_data else []
    rows = [
        create_bolded_row_data(
            CITY_COLUMN_TITLES + extra_titles,
        ),
        create_bolded_row_data(["NON-SPONSORS"]),
    ]
    for non_sponsor in non_sponsors:
        rows.append(
            _create_state_representative_row(
                non_sponsor.person, bill, import_data
            )
        )

    rows.append(create_row_data([]))
    rows.append(create_bolded_row_data(["SPONSORS"]))

    for sponsorship in sponsorships:
        rows.append(
            _create_state_representative_row(
                sponsorship.senator.person,
                bill,
                import_data,
                sponsorship.is_lead_sponsor,
            )
        )

    return rows


def get_sort_key(council_member):
    sort_key = BOROUGH_SORT_TABLE.get(
        council_member.borough, len(BOROUGH_SORT_TABLE)
    )
    return (sort_key, council_member.person.name)


def _get_sponsor_name_text(legislator_name, is_lead):
    return f"{legislator_name}{' (lead)' if is_lead else ''}"


def _create_city_power_hour(bill, sheet_title, import_data):
    sponsorships = bill.city_bill.sponsorships
    sponsorships = sorted(
        sponsorships, key=lambda s: get_sort_key(s.council_member)
    )

    sponsor_ids = [s.council_member_id for s in sponsorships]
    non_sponsors = CouncilMember.query.filter(
        CouncilMember.person_id.not_in(sponsor_ids)
    ).all()
    non_sponsors = sorted(non_sponsors, key=get_sort_key)

    row_data = _create_city_power_hour_row_data(
        bill.city_bill,
        sponsorships,
        non_sponsors,
        import_data,  # unclear this needs to pass city_bill
    )

    return create_spreadsheet(sheet_title, row_data, CITY_COLUMN_WIDTHS)


def _create_state_power_hour(bill, sheet_title, import_data):
    # Make sure this works if only one of senate or assembly bill are defined
    senate_bill = bill.state_bill.senate_bill
    assembly_bill = bill.state_bill.assembly_bill

    if senate_bill:
        senate_sponsorships = senate_bill.sponsorships
        senate_sponsor_ids = [s.person_id for s in senate_sponsorships]
        senate_non_sponsors = Senator.query.filter(
            Senator.person_id.not_in(senate_sponsor_ids)
        ).all()
        # TODO repeat for assembly, make generic
    else:
        senate_sponsorships = []
        senate_non_sponsors = []

    row_data = _create_state_power_hour_row_data(
        bill, senate_sponsorships, senate_non_sponsors, import_data
    )

    return create_spreadsheet(
        sheet_title, row_data, []
    )  # TODO: DO  state column widths


def create_power_hour(
    bill_id: UUID, title: str, old_spreadsheet_to_import: str
) -> Tuple[Dict, List[str]]:
    """Creates a spreadsheet that's a template to run a phone bank
    for a specific bill, based on its current sponsors. The sheet will be
    owned by a robot Google account and will be made publicly editable by
    anyone with the link."""
    bill = Bill.query.filter_by(id=bill_id).one()

    logging.info(
        f"Creating new power hour titled {title}, importing old spreadsheet {old_spreadsheet_to_import}"
    )
    if old_spreadsheet_to_import:
        import_data = _extract_data_from_previous_power_hour(
            old_spreadsheet_to_import
        )
    else:
        import_data = None

    if bill.type == Bill.BillType.CITY:
        spreadsheet_result = _create_city_power_hour(bill, title, import_data)
    else:
        spreadsheet_result = _create_state_power_hour(bill, title, import_data)

    output_messages = import_data.import_messages if import_data else []
    output_messages.append("Spreadsheet was created")

    return (spreadsheet_result, output_messages)


def _extract_data_from_previous_spreadsheet(
    spreadsheet_cells,
) -> PowerHourImportData:
    import_messages = []

    if not spreadsheet_cells:
        return PowerHourImportData(None, None, ["Old spreadsheet was empty"])

    title_row = spreadsheet_cells[0]
    data_rows = spreadsheet_cells[1:]

    # Look through the column titles, pick out the Name column and any other
    # columns that aren't part of the standard set. We'll copy those over.
    extra_column_title_indices: Tuple[int, str] = []
    name_column_index = None
    for i, title in enumerate(title_row):
        if title not in CITY_COLUMN_TITLE_SET:
            extra_column_title_indices.append((i, title))
        elif title == "Name":
            name_column_index = i

    if name_column_index is None:
        import_messages.append(
            "Could not find a 'Name' column at the top of the old spreadsheet, so nothing was copied over"
        )
        logging.warning(
            f"Could not find Name column in spreadsheet. Title columns were {','.join(title_row)}"
        )
        return PowerHourImportData(None, None, import_messages)

    extra_columns_by_council_member_name: Dict[str, Dict[str, str]] = {}
    for row in data_rows:
        # Ignore empty rows, which may have fewer cells in the array
        if (
            name_column_index < len(row)
            and (name := row[name_column_index]) is not None
        ):
            legislator_extra_columns: Dict[str, str] = {}
            for index, extra_column_title in extra_column_title_indices:
                if index < len(row):
                    legislator_extra_columns[extra_column_title] = row[index]
            extra_columns_by_council_member_name[
                name
            ] = legislator_extra_columns

    titles = [column[1] for column in extra_column_title_indices]
    if titles:
        for title in titles:
            import_messages.append(f"Copied column '{title}' to new sheet")
    else:
        import_messages.append(
            "Did not find any extra columns in the old sheet to import"
        )

    # Now rekey by legislator ID
    # TODO: I think I need to change this so that it's by person_id, not the council_id
    council_members = CouncilMember.query.all()
    column_data_by_council_member_id: Dict[UUID, Dict[str, str]] = {}
    for council_member in council_members:
        council_member_data = extra_columns_by_council_member_name.get(
            council_member.person.name
        )
        if council_member_data is None:
            council_member_data = extra_columns_by_council_member_name.get(
                _get_sponsor_name_text(council_member.person.name, True)
            )
        if council_member_data is not None:
            column_data_by_council_member_id[
                council_member.person_id
            ] = council_member_data
        else:
            import_messages.append(
                f"Could not find {council_member.person.name} under the Name column in the old sheet. Make sure the name matches exactly."
            )

    return PowerHourImportData(
        extra_column_titles=titles,
        column_data_by_legislator_id=column_data_by_council_member_id,
        import_messages=import_messages,
    )


def _extract_data_from_previous_power_hour(
    spreadsheet_id,
) -> Optional[PowerHourImportData]:
    """Reads cells from the spreadsheet of a previous power hour and extracts
    some data that should be copied into the next power hour, to preserve context
    for new callers. It follows these rules:
      * First it seeks to find the row for each legislator. It searches for a Name
        column, and then does an exact string match of the legislator name within
        that column.
      * For each legislator, it imports data for all *extra columns* that aren't one
        of the autogenerated ones. In other words, columns that were added when
        customizing the spreadsheet after it was generated.
    """

    spreadsheet_cells = get_spreadsheet_cells(spreadsheet_id)
    return _extract_data_from_previous_spreadsheet(spreadsheet_cells)
