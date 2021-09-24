import logging

from .council_api import get_bill, get_current_council_members, get_person, get_bill_sponsors
from .models import Bill, Legislator, db, BillSponsorship


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


def add_council_members():
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


def fill_council_person_data():
    legislators = Legislator.query.all()

    for legislator in legislators:
        data = get_person(legislator.id)
        legislator.email = data["PersonEmail"]
        legislator.district_phone = data["PersonPhone"]
        legislator.legislative_phone = data["PersonPhone2"]

    db.session.commit()


def update_sponsorships(bill_id):
    sponsorships = get_bill_sponsors(bill_id)

    existing_legislators = Legislator.query.filter(Legislator.id.in_(
        [s['MatterSponsorNameId'] for s in sponsorships]
    )).all()
    existing_legislator_ids = set([l.id for l in existing_legislators])

    for sponsorship in sponsorships:
        legislator_id = sponsorship['MatterSponsorNameId']
        if legislator_id not in existing_legislator_ids:
            logging.warning(f"Did not find legislator {legislator_id} in db, ignoring...")
            continue
            # TODO: Instead, insert a stub for them or something
    
        internal_sponsorship = BillSponsorship(bill_id=bill_id, legislator_id=legislator_id)
        db.session.merge(internal_sponsorship)
    
    db.session.commit()


def update_all_sponsorships():
    bills = Bill.query.all()
    for bill in bills:
        logging.info(f"Updating sponsorships for bill {bill.id} {bill.name}")
        update_sponsorships(bill.id)
