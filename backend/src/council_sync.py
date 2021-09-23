from .council_api import find_bill
from .models import Bill, db
from sqlalchemy import update
import logging


def add_or_update_bill(intro_name):
    logging.info(f"Add or update bill for {intro_name}")
    matter = find_bill(intro_name)

    data = {
      "id": matter['MatterId'],
      "file": matter["MatterFile"],
      "name": matter["MatterName"],
      "title": matter["MatterTitle"],
      "body": matter["MatterBodyName"],
      "intro_date": matter["MatterIntroDate"],
      "status": matter["MatterStatusName"],
    }

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