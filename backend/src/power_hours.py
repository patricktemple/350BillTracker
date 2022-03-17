import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union

from . import twitter
from .bill.models import Bill
from .google_sheets import (
    Cell,
    Color,
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

# Title and width in pixels for each column. We can't dynamically set it to match the,
# contents via the API, so instead we just hardcode the width as best we can.
CITY_COLUMN_TITLES = [
    ("Name", 150),
    ("Sponsor", 75),
    ("Email", 200),
    ("Party", 50),
    ("Borough", 100),
    ("District Phone", 100),
    ("Legislative Phone", 100),
    ("Twitter", 150),
    ("Committees", 200),
    ("Staffers", 250),
    ("Search for relevant tweets to bill", 250),
]
CITY_COLUMN_TITLE_SET = {t[0] for t in CITY_COLUMN_TITLES}

STATE_COLUMN_TITLES = [
    ("Name", 150),
    ("Sponsor", 75),
    ("Chamber", 75),
    ("Email", 200),
    ("Party", 50),
    ("District", 60),
    ("District Contact", 200),
    ("Albany Contact", 200),
    ("Twitter", 150),
    ("Staffers", 250),
    ("Search for relevant tweets to bill", 100),
]
STATE_COLUMN_TITLE_SET = {t[0] for t in STATE_COLUMN_TITLES}

BOROUGH_SORT_TABLE = {
    "Brooklyn": 0,
    "Manhattan": 1,
    "Manhattan and Bronx": 2,
    "Queens": 3,
    "Bronx": 4,
    "Staten Island": 5,
}


@dataclass
class PowerHourImportData:
    """Data about a previous power hour that will be copied into a new sheet."""

    extra_column_titles: List[str]
    column_data_by_person_id: Dict[id, Dict[str, str]]
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
    legislator_data = import_data.column_data_by_person_id.get(person.id)
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
    *,
    is_sponsor: bool,
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
        Cell(
            _get_sponsor_name_text(council_member.person.name, is_lead_sponsor)
        ),
        _format_sponsor_status(is_sponsor),
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


def _format_office_contacts(office_contacts: List[OfficeContact]):
    office_strings = []
    for office_contact in office_contacts:
        single_office_lines = [f"----- {office_contact.city} -----"]
        if office_contact.phone:
            single_office_lines.append(f"Phone: {office_contact.phone}")
        if office_contact.fax:
            single_office_lines.append(f"Fax: {office_contact.fax}")
        office_strings.append("\n".join(single_office_lines))

    return "\n\n".join(office_strings)


def _format_sponsor_status(sponsored: bool):
    if sponsored:
        return Cell(value="Yes", color=Color.Green)

    return Cell(value="No", color=Color.Red)


def _create_state_representative_row(
    representative: Union[Senator, AssemblyMember],
    bill: Bill,
    import_data: Optional[PowerHourImportData],
    *,
    is_sponsor: bool,
    is_lead_sponsor: bool = False,
):
    person = representative.person
    staffer_strings = [
        _get_staffer_display_string(s) for s in person.staffer_persons
    ]
    staffer_text = "\n\n".join(staffer_strings)

    twitter_search_url = twitter.get_bill_twitter_search_url(bill, person)

    if person.type == Person.PersonType.SENATOR:
        chamber_name = "Senate"
        district = f"S-{representative.district}"
    else:
        chamber_name = "Assembly"
        district = f"A-{representative.district}"

    albany_contacts = _format_office_contacts(
        (
            c
            for c in person.office_contacts
            if c.type == OfficeContact.OfficeContactType.CENTRAL_OFFICE
        )
    )
    district_contacts = _format_office_contacts(
        (
            c
            for c in person.office_contacts
            if c.type == OfficeContact.OfficeContactType.DISTRICT_OFFICE
        )
    )

    cells = [
        Cell(_get_sponsor_name_text(person.name, is_lead_sponsor)),
        _format_sponsor_status(is_sponsor),
        Cell(chamber_name),
        Cell(person.email),
        Cell(person.party or ""),
        Cell(district, link_url=representative.website),
        Cell(district_contacts),
        Cell(albany_contacts),
        Cell(
            person.display_twitter or "",
            link_url=person.twitter_url,
        ),
        Cell(staffer_text),
        Cell(
            "Relevant tweets" if twitter_search_url else "",
            link_url=twitter_search_url,
        ),
    ]
    if import_data:
        cells.extend(_get_imported_data_cells(person, import_data))

    return create_row_data(cells)


def _create_city_power_hour_row_data(
    bill: Bill,
    sponsorships: List[CitySponsorship],
    non_sponsors: List[CouncilMember],
    import_data: Optional[PowerHourImportData],
):
    """Generates the full body payload that the Sheets API requires for a
    city phone bank spreadsheet."""

    extra_titles = import_data.extra_column_titles if import_data else []
    rows = [
        create_bolded_row_data(
            [title for title, _ in CITY_COLUMN_TITLES] + extra_titles,
        ),
    ]
    for non_sponsor in non_sponsors:
        rows.append(
            _create_council_member_row(
                non_sponsor, bill, import_data, is_sponsor=False
            )
        )

    for sponsorship in sponsorships:
        rows.append(
            _create_council_member_row(
                sponsorship.council_member,
                bill,
                import_data,
                is_sponsor=True,
                is_lead_sponsor=sponsorship.sponsor_sequence == 0,
            )
        )

    return rows


def _create_state_power_hour_row_data(
    bill: Bill,
    sponsorships: List[Union[SenateSponsorship, AssemblySponsorship]],
    non_sponsors: List[Union[Senator, AssemblyMember]],
    import_data: Optional[PowerHourImportData],
):
    """Generates the full body payload that the Sheets API requires for a
    state phone bank spreadsheet."""

    extra_titles = import_data.extra_column_titles if import_data else []
    rows = [
        create_bolded_row_data(
            [title for title, _ in STATE_COLUMN_TITLES] + extra_titles,
        ),
    ]
    for non_sponsor in non_sponsors:
        rows.append(
            _create_state_representative_row(
                non_sponsor, bill, import_data, is_sponsor=False
            )
        )
    for sponsorship in sponsorships:
        rows.append(
            _create_state_representative_row(
                sponsorship.representative,
                bill,
                import_data,
                is_sponsor=True,
                is_lead_sponsor=sponsorship.is_lead_sponsor,
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
        bill,
        sponsorships,
        non_sponsors,
        import_data,
    )

    return create_spreadsheet(
        sheet_title, row_data, [width for _, width in CITY_COLUMN_TITLES]
    )


def _create_state_power_hour(bill, sheet_title, import_data):
    senate_bill = bill.state_bill.senate_bill
    assembly_bill = bill.state_bill.assembly_bill

    sponsorships = []
    non_sponsors = []

    # TODO: Factor out non_sponsors into the view. It's used all over.
    if senate_bill:
        sponsorships.extend(senate_bill.sponsorships)
        senate_sponsor_ids = [s.person_id for s in senate_bill.sponsorships]
        senate_non_sponsors = Senator.query.filter(
            Senator.person_id.not_in(senate_sponsor_ids)
        )
        non_sponsors.extend(senate_non_sponsors)
    if assembly_bill:
        sponsorships.extend(assembly_bill.sponsorships)
        assembly_sponsor_ids = [
            s.person_id for s in assembly_bill.sponsorships
        ]
        assembly_non_sponsors = AssemblyMember.query.filter(
            AssemblyMember.person_id.not_in(assembly_sponsor_ids)
        )
        non_sponsors.extend(assembly_non_sponsors)

    row_data = _create_state_power_hour_row_data(
        bill, sponsorships, non_sponsors, import_data
    )

    return create_spreadsheet(
        sheet_title, row_data, [width for _, width in STATE_COLUMN_TITLES]
    )


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
        if bill.type == Bill.BillType.CITY:
            import_data = _extract_data_from_previous_power_hour(
                old_spreadsheet_to_import,
                CITY_COLUMN_TITLE_SET,
                [Person.PersonType.COUNCIL_MEMBER],
            )
        else:
            person_types = []
            if bill.state_bill.senate_bill:
                person_types.append(Person.PersonType.SENATOR)
            if bill.state_bill.assembly_bill:
                person_types.append(Person.PersonType.ASSEMBLY_MEMBER)
            import_data = _extract_data_from_previous_power_hour(
                old_spreadsheet_to_import,
                STATE_COLUMN_TITLE_SET,
                person_types,
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
    standard_column_titles: Set[str],
    person_types: List[Person.PersonType],
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
        if title not in standard_column_titles:
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
    persons = Person.query.filter(Person.type.in_(person_types)).all()
    person_data_by_id: Dict[UUID, Dict[str, str]] = {}
    for person in persons:
        person_data = extra_columns_by_council_member_name.get(person.name)
        if person_data is None:
            # If they're the lead sponsor, their name is formatted differently, so try
            # that as well.
            person_data = extra_columns_by_council_member_name.get(
                _get_sponsor_name_text(person.name, True)
            )
        if person_data is not None:
            person_data_by_id[person.id] = person_data
        else:
            import_messages.append(
                f"Could not find {person.name} under the Name column in the old sheet. Make sure the name matches exactly."
            )

    return PowerHourImportData(
        extra_column_titles=titles,
        column_data_by_person_id=person_data_by_id,
        import_messages=import_messages,
    )


def _extract_data_from_previous_power_hour(
    spreadsheet_id: str,
    standard_column_titles: Set[str],
    person_types: List[Person.PersonType],
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
    return _extract_data_from_previous_spreadsheet(
        spreadsheet_cells, standard_column_titles, person_types
    )
