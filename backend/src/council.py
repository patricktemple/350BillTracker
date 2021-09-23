from datetime import date

import requests

from src.settings import CITY_COUNCIL_API_TOKEN


def council_get(path, *, params=None):
    if not params:
        params = {}
    return requests.get(
        f"https://webapi.legistar.com/v1/nyc/{path}",
        params={"token": CITY_COUNCIL_API_TOKEN, **params},
    )


def date_filter(field, operator, date):
    return f"{field} {operator} datetime'{date.isoformat()}'"


def make_filter_param(*filters):
    return {"$filter": " and ".join(filters)}


# http://webapi.legistar.com/Help/Api/GET-v1-Client-Matters
def get_matters():
    return council_get(
        "matters",
        params=make_filter_param(
            date_filter("MatterIntroDate", "ge", date(2021, 1, 1)),
            "MatterTypeName eq 'Introduction'"
        ),
    ).json()
