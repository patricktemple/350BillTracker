import logging
from datetime import datetime, timezone

from requests import HTTPError

from .bill.models import Bill
from .council_api import (
    get_bill_sponsors,
    get_current_council_members,
    get_person,
    lookup_bill,
)
from .person.models import Person, CouncilMember
from .models import db
from .sponsorship.models import CitySponsorship
from .static_data import COUNCIL_DATA_BY_LEGISLATOR_ID
from .utils import now



def add_council_members():
    """Adds basic information about each current council member based on their
    OfficeRecord object in the API. This is missing key fields that need
    to be filled in with other sources."""
    members = get_current_council_members()

    for member in members:
        person = Person(type=Person.PersonType.COUNCIL_MEMBER,
            name=member["OfficeRecordFullName"],
            title="City Council Member", # TODO
        )
        person.council_member = CouncilMember(
            city_council_person_id=member["OfficeRecordPersonId"],
            term_start=datetime.fromisoformat(
                member["OfficeRecordStartDate"]
            ).replace(tzinfo=timezone.utc),
            term_end=datetime.fromisoformat(
                member["OfficeRecordEndDate"]
            ).replace(tzinfo=timezone.utc),
        )
        # TODO: Merge is probably not concurrency friendly. Do insert+on_conflict_do_update
        # TODO figure out if merge works with this nested data
        db.session.merge(person)

    db.session.commit()


def fill_council_person_data_from_api():
    """For all council members in the DB, updates their contact info and other details
    based on the Person API and our own static data.
    """
    council_members = CouncilMember.query.all()

    # TODO make sure the query joined loads the persons
    for council_member in council_members:
        try:
            data = get_person(council_member.city_council_person_id)
            council_member.person.email = data["PersonEmail"]
            council_member.person.phone = data["PersonPhone"]
            council_member.phone = data["PersonPhone2"]
            council_member.website = data["PersonWWW"]
            # Borough exists here but we prefer the cleaned static data
        except HTTPError:
            logging.exception(f"Could not get Person {council_member.city_council_person_id} from API")
            continue

    db.session.commit()


def fill_council_person_static_data():
    council_members = CouncilMember.query.all()

    for council_member in council_members:
        member_data = COUNCIL_DATA_BY_LEGISLATOR_ID.get(council_member.city_council_person_id)
        if not member_data:
            logging.warning(
                f"Found a legislator without static data: {council_member.city_council_person_id} {council_member.person.name}"
            )
        else:
            council_member.person.twitter = member_data["twitter"]
            council_member.person.party = member_data["party"]

            # Name and borough both exist in the API but the static data has a
            # cleaned-up version.
            council_member.person.name = member_data["name"]
            council_member.borough = member_data["borough"]

    legislator_ids_from_db = set([l.city_council_person_id for l in council_members])
    if diff := set(COUNCIL_DATA_BY_LEGISLATOR_ID.keys()).difference(
        legislator_ids_from_db
    ):
        unmatched_static_data = [
            COUNCIL_DATA_BY_LEGISLATOR_ID[id] for id in diff
        ]
        logging.warning(
            f"Static data has some legislators not in the DB: {unmatched_static_data}"
        )

    db.session.commit()


# Bills ----------------------------------------------------------------------


def _update_bill(bill_id):
    # TODO: Update this to do council specific bill object too
    # bill_data = lookup_bill(bill_id)
    # logging.info(f"Updating bill {bill_id} and got {bill_data}")

    # Bill.query.filter_by(id=bill_id).one()  # ensure bill exists
    # db.session.merge(Bill(**bill_data))
    pass


def sync_bill_updates():
    # bills = Bill.query.all()

    # for bill in bills:
    #     _update_bill(bill.id)
    #     db.session.commit()
    pass


def update_bill_sponsorships(bill_id, set_added_at=False):
    """
    Updates sponsorships for a given bill:
    1) Deletes any previous sponsorships
    2) Adds all new sponsorships
    3) If new sponsors aren't in the existing legislators (e.g. they're not longer in office),
       ignore them.
    """
    # existing_sponsorships = BillSponsorship.query.filter_by(
    #     bill_id=bill_id
    # ).all()
    # existing_sponsorships_by_id = {
    #     s.legislator_id: s for s in existing_sponsorships
    # }

    # new_sponsorships = get_bill_sponsors(bill_id)

    # existing_legislators = CouncilMember.query.filter(
    #     CouncilMember.id.in_([s["MatterSponsorNameId"] for s in new_sponsorships])
    # ).all()
    # existing_legislator_ids = {l.id for l in existing_legislators}

    # for sponsorship in new_sponsorships:
    #     legislator_id = sponsorship["MatterSponsorNameId"]

    #     if legislator_id not in existing_legislator_ids:
    #         # Can't insert the sponsorship without its foreign key object
    #         # TODO: Instead, insert a stub for them or something
    #         logging.warning(
    #             f"Did not find legislator {legislator_id} in db, ignoring..."
    #         )
    #         continue

    #     internal_sponsorship = BillSponsorship(
    #         bill_id=bill_id,
    #         legislator_id=legislator_id,
    #         sponsor_sequence=sponsorship["MatterSponsorSequence"],
    #     )

    #     if legislator_id in existing_sponsorships_by_id:
    #         # Remove sponsors from this set until we're left with only those
    #         # sponsorships that were rescinded recently.
    #         del existing_sponsorships_by_id[legislator_id]
    #     elif set_added_at:
    #         internal_sponsorship.added_at = now()

    #     db.session.merge(internal_sponsorship)

    # for lost_sponsor in existing_sponsorships_by_id.values():
    #     db.session.delete(lost_sponsor)


def update_all_sponsorships():
    bills = Bill.query.all()
    for bill in bills:
        logging.info(f"Updating sponsorships for bill {bill.id} {bill.name}")
        update_bill_sponsorships(bill.id, set_added_at=True)
        db.session.commit()
