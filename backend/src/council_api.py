from datetime import date

import requests

from src.settings import CITY_COUNCIL_API_TOKEN

from .utils import now

# See http://webapi.legistar.com/Help for an overview of resources.


def council_get(path, *, params=None):
    if not params:
        params = {}
    return requests.get(
        f"https://webapi.legistar.com/v1/nyc/{path}",
        params={"token": CITY_COUNCIL_API_TOKEN, **params},
    )


def date_filter(field, operator, date):
    return f"{field} {operator} datetime'{date.isoformat()}'"


def eq_filter(field, value):
    return f"{field} eq '{value}'"


def make_filter_param(*filters):
    return {"$filter": " and ".join(filters)}


# http://webapi.legistar.com/Help/Api/GET-v1-Client-Matters
def get_recent_bills():
    return council_get(
        "matters",
        params=make_filter_param(
            date_filter("MatterIntroDate", "ge", date(2021, 1, 1)),
            eq_filter("MatterTypeName", "Introduction"),
        ),
    ).json()


def lookup_bills(file_name):
    # intro_name should be something like 2317-2021 including the year
    # TODO: Escape the name
    return council_get(
        "matters",
        params=make_filter_param(
            eq_filter("MatterTypeName", "Introduction"),
            f"substringof('{file_name}', MatterFile) eq true",
        ),
    ).json()


def get_bill(matter_id):
    return council_get(
        f"matters/{matter_id}",
    ).json()


def get_bill_sponsors(matter_id):
    return council_get(
        f"matters/{matter_id}/sponsors",
    ).json()


def get_person(person_id):
    return council_get(f"persons/{person_id}").json()


def get_current_council_members():
    office_records = council_get(
        "officerecords",
        params=make_filter_param(
            eq_filter("OfficeRecordBodyName", "City Council"),
            date_filter("OfficeRecordStartDate", "le", now().date()),
            date_filter("OfficeRecordEndDate", "ge", now().date()),
        ),
    ).json()

    return office_records

# TODO: Handle errors on all these APIs. A bunch seem to fail midway through.