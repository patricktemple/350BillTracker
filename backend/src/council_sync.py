import logging

from requests import HTTPError

from .council_api import (
    lookup_bill,
    get_bill_sponsors,
    get_current_council_members,
    get_person,
)
from .models import Bill, BillSponsorship, Legislator, db
from .static_data import STATIC_DATA_BY_LEGISLATOR_ID
from sqlalchemy.orm import selectinload


# Legislators ----------------------------------------------------------------


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


# Bills ----------------------------------------------------------------------


class BillSnapshot:
    bill_id = None
    status = None
    sponsor_ids = []

    def __init__(self, bill_id, status, sponsor_ids):
        self.bill_id = bill_id # needed?
        self.status = status
        self.sponsor_ids = sponsor_ids


def snapshot_bills():
    """Snapshots the state of all bills. Used to calculate the diff produced by
    a cron job run, so that we can send out email notifications of bill status changes."""
    bills = Bill.query.options(selectinload(Bill.sponsorships)).all()

    snapshots_by_bill_id = {}
    for bill in bills:
        sponsor_ids = [s.legislator_id for s in bill.sponsorships]
        snapshot = BillSnapshot(bill.id, bill.status, sponsor_ids)
        snapshots_by_bill_id[bill.id] = snapshot


    return snapshots_by_bill_id


def update_bill(bill_id):
    bill_data = lookup_bill(bill_id)
    logging.info(f"Updating bill {bill_id} and got {bill_data}")

    existing_bill = Bill.query.filter_by(id=bill_id).one()
    db.session.merge(Bill(**bill_data))
    db.session.commit()


def sync_bill_updates():
    bills = Bill.query.all()

    for bill in bills:
        update_bill(bill.id)


# TODO: Unit test this whole cron job
def update_sponsorships(bill_id):
    # TODO: This does not remove sponsorships if they're taken away! Implement and test that
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
