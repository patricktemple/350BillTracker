from datetime import datetime, timezone

import requests

from src.settings import CITY_COUNCIL_API_TOKEN

from .bill.models import Bill
from .utils import now

from typing import List
import logging

# See http://webapi.legistar.com/Help for an overview of resources.


def council_get(path, *, params=None):
    if not params:
        params = {}
    response = requests.get(
        f"https://webapi.legistar.com/v1/nyc/{path}",
        params={"token": CITY_COUNCIL_API_TOKEN, **params},
    )
    response.raise_for_status()
    return response.json()


def date_filter(field, operator, date):
    return f"{field} {operator} datetime'{date.isoformat()}'"


def eq_filter(field, value):
    return f"{field} eq '{value}'"


def make_filter_param(*filters):
    return {"$filter": " and ".join(filters)}


def _convert_matter_to_bill(matter):
    """Converts the City Council's representation of a bill, called Matters,
    into our own format."""
    return {
        "type": Bill.BillType.CITY,
        "name": matter["MatterName"],
        "description": matter["MatterTitle"],
        "city_bill": {
            "file": matter["MatterFile"],
            "council_body": matter["MatterBodyName"],
            "city_bill_id": matter["MatterId"],
            "intro_date": datetime.fromisoformat(
                matter["MatterIntroDate"]
            ).replace(tzinfo=timezone.utc),
            "status": matter["MatterStatusName"],
            "active_version": matter["MatterVersion"],
        },
    }


def lookup_bills(file_name):
    matters = council_get(
        "matters",
        params=make_filter_param(
            # "Introduction" means "bill". Matters can be other things like "Motion".
            eq_filter("MatterTypeName", "Introduction"),
            f"substringof('{file_name}', MatterFile) eq true",
        ),
    )
    return [_convert_matter_to_bill(m) for m in matters]


def lookup_bill(matter_id):
    matter = council_get(
        f"matters/{matter_id}",
    )
    return _convert_matter_to_bill(matter)


def get_bill_sponsors(matter_id, active_version):
    sponsors = council_get(
        f"matters/{matter_id}/sponsors",
    )

    # The sponsorships for various amendments will appear in a flat list, and we only care
    # about the active version.
    return [
        s
        for s in sponsors
        if s["MatterSponsorMatterVersion"] == active_version
    ]


def get_person(person_id):
    return council_get(f"persons/{person_id}")


def get_current_council_members():
    return council_get(
        "officerecords",
        params=make_filter_param(
            eq_filter("OfficeRecordBodyName", "City Council"),
            date_filter("OfficeRecordStartDate", "le", now().date()),
            date_filter("OfficeRecordEndDate", "ge", now().date()),
        ),
    )


# Unify office records
def get_current_committee_memberships(committee_body_ids: List[int]):
    # An alternate way to filter is to check that OfficeRecordTitle is either 'CHAIRPERSON' or 'Committee Member'.
    # However, this way lets us restrict to the committees that exist in the DB, and could flexibly include new
    # titles in the future.
    records = council_get(
        "officerecords",
        params=make_filter_param(
            # eq_filter("OfficeRecordBodyName", "City Council"),
            date_filter("OfficeRecordStartDate", "le", now().date()),
            date_filter("OfficeRecordEndDate", "ge", now().date()),
        ),
    )
    if len(records) >= 1000:
        logging.error(">=1000 office records returned. This may be getting truncated by lack of pagination")


def get_committees():
    bodies = council_get(
        "bodies",
    )

    # It's weird that Committee on Land Use has a type of Land Use instead of committee
    committee_types = { "Committee", "Subcommittee", "Land Use" }

    # For reference, the other active body types in 2022 were:
    # Primary Legislative Body
    # Charter Revision Commission 2019
    # New York City Advisory Commission on Property Tax Reform
    # Democratic Conference of the Council of the City of New York 
    # Manhattan Borough Board 
    # Minority (Republican) Conference of the Council of the City of New York 
    # Withdrawn
    # Special Committee

    return [b for b in bodies if b['BodyActiveFlag'] and b['BodyTypeName'] in committee_types], bodies