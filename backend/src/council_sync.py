import logging

from requests import HTTPError

from .council_api import (
    get_bill,
    get_bill_sponsors,
    get_current_council_members,
    get_person,
)
from .models import Bill, BillSponsorship, Legislator, db
from .static_data import STATIC_DATA_BY_LEGISLATOR_ID


def convert_matter_to_bill(matter):
    return {
        "id": matter["MatterId"],
        "file": matter["MatterFile"],
        "name": matter["MatterName"],
        "title": matter["MatterTitle"],
        "body": matter["MatterBodyName"],
        "intro_date": matter["MatterIntroDate"],
        "status": matter["MatterStatusName"],
    }


def add_or_update_bill(matter_id):
    bill_data = get_bill(matter_id)
    logging.info(f"Got bill {bill_data} for {matter_id}")
    upsert_matter_data(bill_data)


def upsert_matter_data(matter_json):
    logging.info("Add or update bill")

    data = convert_matter_to_bill(matter_json)
    existing_bill = Bill.query.get(data["id"])
    if existing_bill:
        logging.info(f"Bill {data['file']} already in DB, updating")
    else:
        logging.info(f"Bill {data['file']} not found in DB, adding")
    db.session.merge(Bill(**data))
    db.session.commit()


def sync_bill_updates():
    bills = Bill.query.all()

    for bill in bills:
        add_or_update_bill(bill.id)


def add_council_members():
    """Adds basic information about each current council member based on their
    OfficeRecord object in the API. This is missing key fields that need
    to be filled in with other sources."""
    members = get_current_council_members()

    for member in members:
        legislator = Legislator(
            name=member["OfficeRecordFullName"],
            id=member["OfficeRecordPersonId"],
            term_start=member["OfficeRecordStartDate"],
            term_end=member["OfficeRecordEndDate"],
        )
        # TODO: Merge is probably not concurrency friendly. Do insert+on_conflict_do_update
        db.session.merge(legislator)

    db.session.commit()


def convert_borough(city_name):
    if city_name == "New York":
        return "Manhattan"
    return city_name


def fill_council_person_data():
    """For all council members in the DB, updates their contact info and other details
    based on the Person API and our own static data.
    """
    legislators = Legislator.query.all()

    for legislator in legislators:
        try:
            data = get_person(legislator.id)
            legislator.email = data["PersonEmail"]
            legislator.district_phone = data["PersonPhone"]
            legislator.legislative_phone = data["PersonPhone2"]
            legislator.borough = convert_borough(data["PersonCity1"])
            legislator.website = data["PersonWWW"]
        except HTTPError as e:
            logging.exception(f"Could not get Person {legislator.id} from API")
            continue

    for legislator in legislators:
        legislator_data = STATIC_DATA_BY_LEGISLATOR_ID.get(legislator.id)
        if not legislator_data:
            logging.warning(
                f"Found a legislator without static data: {legislator.id} {legislator.name}"
            )
        else:
            legislator.twitter = legislator_data["twitter"]
            legislator.party = legislator_data["party"]

            # Name exists in both sets but we can override it here so we can set
            # a more user-friendly name than some of the formal name in the data.
            legislator.name = legislator_data["name"]

    legislator_ids_from_db = set([l.id for l in legislators])
    if diff := set(STATIC_DATA_BY_LEGISLATOR_ID.keys()).difference(
        legislator_ids_from_db
    ):
        unmatched_static_data = [
            STATIC_DATA_BY_LEGISLATOR_ID[id] for id in diff
        ]
        logging.warning(
            f"Static data has some legislators not in the DB: {unmatched_static_data}"
        )

    db.session.commit()


def update_sponsorships(bill_id):
    sponsorships = get_bill_sponsors(bill_id)

    existing_legislators = Legislator.query.filter(
        Legislator.id.in_([s["MatterSponsorNameId"] for s in sponsorships])
    ).all()
    existing_legislator_ids = set([l.id for l in existing_legislators])

    for sponsorship in sponsorships:
        legislator_id = sponsorship["MatterSponsorNameId"]
        if legislator_id not in existing_legislator_ids:
            logging.warning(
                f"Did not find legislator {legislator_id} in db, ignoring..."
            )
            continue
            # TODO: Instead, insert a stub for them or something

        internal_sponsorship = BillSponsorship(
            bill_id=bill_id, legislator_id=legislator_id
        )

        db.session.merge(internal_sponsorship)

    db.session.commit()


def update_all_sponsorships():
    bills = Bill.query.all()
    for bill in bills:
        logging.info(f"Updating sponsorships for bill {bill.id} {bill.name}")
        update_sponsorships(bill.id)
