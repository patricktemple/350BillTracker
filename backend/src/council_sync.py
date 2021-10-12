import logging

from requests import HTTPError
from sqlalchemy.orm import selectinload

from .council_api import (
    get_bill_sponsors,
    get_current_council_members,
    get_person,
    lookup_bill,
)
from .models import Bill, BillSponsorship, Legislator, db
from .static_data import STATIC_DATA_BY_LEGISLATOR_ID
from .utils import now
from datetime import datetime, timezone

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
            term_start=datetime.fromisoformat(member["OfficeRecordStartDate"]).replace(tzinfo=timezone.utc),
            term_end=datetime.fromisoformat(member["OfficeRecordEndDate"]).replace(tzinfo=timezone.utc),
        )
        # TODO: Merge is probably not concurrency friendly. Do insert+on_conflict_do_update
        db.session.merge(legislator)

    db.session.commit()


def _convert_borough(city_name):
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
            legislator.borough = _convert_borough(data["PersonCity1"])
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
        self.bill_id = bill_id  # needed?
        self.status = status
        self.sponsor_ids = sponsor_ids


# TODO: This file is a weird place for that
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


def _update_bill(bill_id):
    bill_data = lookup_bill(bill_id)
    logging.info(f"Updating bill {bill_id} and got {bill_data}")

    existing_bill = Bill.query.filter_by(id=bill_id).one()
    db.session.merge(Bill(**bill_data))
    db.session.commit()


def sync_bill_updates():
    bills = Bill.query.all()

    for bill in bills:
        _update_bill(bill.id)


# TODO: Unit test this whole cron job
def update_bill_sponsorships(bill_id):
    """
    Updates sponsorships for a given bill:
    1) Deletes any previous sponsorships
    2) Adds all new sponsorships
    3) If new sponsors aren't in the existing legislators (e.g. they're not longer in office),
       ignore them.
    """
    existing_sponsorships = BillSponsorship.query.filter_by(
        bill_id=bill_id
    ).all()
    existing_sponsorships_by_id = {
        s.legislator_id: s for s in existing_sponsorships
    }

    new_sponsorships = get_bill_sponsors(bill_id)

    existing_legislators = Legislator.query.filter(
        Legislator.id.in_([s["MatterSponsorNameId"] for s in new_sponsorships])
    ).all()
    existing_legislator_ids = {l.id for l in existing_legislators}

    for sponsorship in new_sponsorships:
        legislator_id = sponsorship["MatterSponsorNameId"]

        if legislator_id not in existing_legislator_ids:
            # Can't insert the sponsorship without its foreign key object
            # TODO: Instead, insert a stub for them or something
            logging.warning(
                f"Did not find legislator {legislator_id} in db, ignoring..."
            )
            continue

        internal_sponsorship = BillSponsorship(
            bill_id=bill_id, legislator_id=legislator_id
        )

        if legislator_id in existing_sponsorships_by_id:
            # Remove sponsors from this set until we're left with only those
            # sponsorships that were rescinded recently.
            del existing_sponsorships_by_id[legislator_id]
        else:
            internal_sponsorship.added_at = now()

        db.session.merge(internal_sponsorship)

    for lost_sponsor in existing_sponsorships_by_id.values():
        db.session.delete(lost_sponsor)

    db.session.commit()


def update_all_sponsorships():
    bills = Bill.query.all()
    for bill in bills:
        logging.info(f"Updating sponsorships for bill {bill.id} {bill.name}")
        update_bill_sponsorships(bill.id)
