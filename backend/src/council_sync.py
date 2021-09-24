import logging

from sqlalchemy import update

from .council_api import get_bill, get_current_council_members, lookup_bills, get_person
from .models import Bill, Person, db


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
    logging.info(f"Add or update bill")
    # if not bills:
    #     raise ValueError("No matching bill found")
    # if len(bills) > 1:
    #     raise ValueError("Multiple matching bills found!")

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

    # TODO: Lookup their contact info too
    for member in members:
        person = Person(
            name=member["OfficeRecordFullName"],
            id=member["OfficeRecordPersonId"],
            term_start=member["OfficeRecordStartDate"],
            term_end=member["OfficeRecordEndDate"],
        )
        db.session.merge(person)

    db.session.commit()


def fill_council_person_data():
    persons = Person.query.all()

    for person in persons:
        data = get_person(person.id)
        person.email = data['PersonEmail']
        person.district_phone = data['PersonPhone']
        person.legislative_phone = data['PersonPhone2']

    db.session.commit()