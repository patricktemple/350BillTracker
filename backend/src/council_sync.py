from .models import Bill, db
from .council_api import find_bill


def add_bill(intro_name):
    matter = find_bill(intro_name)

    bill = Bill(
        file=matter['MatterFile'],
        name=matter['MatterName'],
        title=matter['MatterTitle'],
        body=matter['MatterBodyName'],
        intro_date=matter['MatterIntroDate'],
        status=matter['MatterStatusName']
    )
    db.session.add(bill)

