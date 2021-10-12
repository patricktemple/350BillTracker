from src.bill_notifications import (
    BillDiff,
    BillSnapshot,
    _calculate_bill_diffs,
    _convert_bill_diff_to_template_variables,
    _get_bill_update_subject_line,
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


def test_email_contents__status_changed():
    bill = add_test_bill(1, "Enacted")
    diff = BillDiff(old_status="Committee", bill=bill)

    subject = _get_bill_update_subject_line([diff])
    assert subject == f"{bill.file}'s status changed to Enacted"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "file": bill.file,
        "display_name": bill.display_name,
        "status_text": "Status: Committee --> Enacted",
        "status_color": "blue",
        "sponsor_text": "0 sponsors (unchanged)",
        "sponsor_color": "black",
    }


def test_email_contents__sponsors_added():
    bill = add_test_bill(1, "Enacted")
    diff = BillDiff(
        old_status="Enacted",
        bill=bill,
        added_sponsors=["Brad Lander", "Jamaal Bowman"],
    )

    for i in range(3):
        add_test_legislator(i)
        add_test_sponsorship(bill_id=1, legislator_id=i)

    db.session.commit()

    subject = _get_bill_update_subject_line([diff])
    assert subject == f"{bill.file} gained 2 sponsors"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "file": bill.file,
        "display_name": bill.display_name,
        "status_text": "Status: Enacted (unchanged)",
        "status_color": "black",
        "sponsor_text": "1 sponsors --> 3 sponsors (gained Brad Lander, Jamaal Bowman)",
        "sponsor_color": "blue",
    }


def test_email_subject__1_sponsor_added():
    bill = add_test_bill(1, "Enacted")
    diff = BillDiff(
        old_status="Enacted",
        bill=bill,
        added_sponsors=["Brad Lander"],
    )

    for i in range(3):
        add_test_legislator(i)
        add_test_sponsorship(bill_id=1, legislator_id=i)

    db.session.commit()

    subject = _get_bill_update_subject_line([diff])
    assert subject == f"{bill.file} gained sponsor Brad Lander"


def test_email_contents__sponsor_removed():
    bill = add_test_bill(1, "Enacted")
    diff = BillDiff(
        old_status="Enacted", bill=bill, removed_sponsors=["Brad Lander"]
    )

    subject = _get_bill_update_subject_line([diff])
    assert subject == f"{bill.file} lost sponsor Brad Lander"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "file": bill.file,
        "display_name": bill.display_name,
        "status_text": "Status: Enacted (unchanged)",
        "status_color": "black",
        "sponsor_text": "1 sponsors --> 0 sponsors (lost Brad Lander)",
        "sponsor_color": "blue",
    }


def test_email_contents__sponsor_added_and_removed():
    bill = add_test_bill(1, "Enacted")
    diff = BillDiff(
        old_status="Enacted",
        bill=bill,
        added_sponsors=["Jamaal Bowman"],
        removed_sponsors=["Brad Lander"],
    )

    add_test_legislator(1)
    add_test_sponsorship(bill_id=1, legislator_id=1)

    db.session.commit()

    subject = _get_bill_update_subject_line([diff])
    assert subject == f"{bill.file} gained and lost sponsors"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "file": bill.file,
        "display_name": bill.display_name,
        "status_text": "Status: Enacted (unchanged)",
        "status_color": "black",
        "sponsor_text": "1 sponsors --> 1 sponsors (gained Jamaal Bowman, lost Brad Lander)",
        "sponsor_color": "blue",
    }
