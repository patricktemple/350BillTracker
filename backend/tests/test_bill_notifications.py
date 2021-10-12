from src.bill_notifications import (
    BillDiff,
    BillSnapshot,
    _calculate_bill_diffs,
)
from src.models import Bill, BillSponsorship, Legislator, db
from src.utils import now


# TODO: Switch to Factory
def add_test_bill(bill_id, status):
    bill = Bill(
        id=bill_id,
        status=status,
        name=f"{bill_id} name",
        file=f"{bill_id} file",
        title=f"{bill_id} title",
        intro_date=now(),
    )
    db.session.add(bill)
    return bill


def add_test_legislator(legislator_id):
    legislator = Legislator(
        id=legislator_id, 
        name=f"{legislator_id} name",
    )
    db.session.add(legislator)
    return legislator


def add_test_sponsorship(*, bill_id, legislator_id):
    sponsorship = BillSponsorship(bill_id=bill_id, legislator_id=legislator_id)
    db.session.add(sponsorship)
    return sponsorship


def test_calculate_bill_diffs():
    snapshots = {
        # This should change status, lose sponsor 2 and gain sponsor 3
        1: BillSnapshot("Committee", [1, 2]),
        # This should be unchanged
        2: BillSnapshot("Enacted", [3]),
    }

    add_test_bill(1, "Enacted")
    add_test_bill(2, "Enacted")
    add_test_legislator(1)
    legislator_2 = add_test_legislator(2)
    legislator_3 = add_test_legislator(3)
    add_test_sponsorship(bill_id=1, legislator_id=1)
    add_test_sponsorship(bill_id=1, legislator_id=3)
    add_test_sponsorship(bill_id=2, legislator_id=3)

    db.session.commit()

    diffs = _calculate_bill_diffs(snapshots)

    assert len(diffs) == 1
    diff = diffs[0]

    assert diff.added_sponsors == [legislator_3.name]
    assert diff.removed_sponsors == [legislator_2.name]
    assert diff.old_status == "Committee"
    assert diff.bill.status == "Enacted"