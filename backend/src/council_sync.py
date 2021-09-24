from .council_api import lookup_bills
from .models import Bill, db
from sqlalchemy import update
import logging


def convert_matter_to_bill(matter):
    return {
      "id": matter['MatterId'],
      "file": matter["MatterFile"],
      "name": matter["MatterName"],
      "title": matter["MatterTitle"],
      "body": matter["MatterBodyName"],
      "intro_date": matter["MatterIntroDate"],
      "status": matter["MatterStatusName"],
    }


def add_or_update_bill(intro_name):
    logging.info(f"Add or update bill for {intro_name}")
    matter = lookup_bills(intro_name)

    # if not bills:
    #     raise ValueError("No matching bill found")
    # if len(bills) > 1:
    #     raise ValueError("Multiple matching bills found!")

    data = convert_matter_to_bill(matter)

    existing_bill = Bill.query.get(data['id'])
    if existing_bill:
        logging.info(f"Bill {intro_name} already in DB, updating")
        for key in data.keys():
            setattr(existing_bill, key, data[key])
    else:
        logging.info(f"Bill {intro_name} not found in DB, adding")
        bill = Bill(**data)
        db.session.add(bill)

    db.session.commit()