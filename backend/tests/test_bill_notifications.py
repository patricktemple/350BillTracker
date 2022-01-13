from unittest.mock import patch
from uuid import uuid4

import responses

from src.app import app
from src.bill.models import AssemblyBill, Bill, CityBill, SenateBill, StateBill
from src.bill_notifications import (
    GenericBillDiff,
    GenericBillSnapshot,
    SnapshotState,
    BillDiffSet,
    _calculate_all_bill_diffs,
    _convert_bill_diff_to_template_variables,
    _get_bill_update_subject_line,
    send_bill_update_notifications,
)
from src.models import db
from src.person.models import CouncilMember, Person
from src.sponsorship.models import CitySponsorship
from src.user.models import User
from src.utils import now


# TODO: Switch to Factory
def add_test_bill(city_bill_id, status) -> Bill:
    bill = Bill(
        id=uuid4(),
        name=f"{city_bill_id} name",
        description="description",
        type=Bill.BillType.CITY,
    )
    bill.city_bill = CityBill(
        city_bill_id=city_bill_id,
        file=f"{city_bill_id} file",
        status=status,
        intro_date=now(),
        active_version="A",
    )
    db.session.add(bill)
    return bill


def add_test_council_member(city_council_person_id) -> Person:
    person = Person(
        id=uuid4(),
        name=f"{city_council_person_id} name",
        type=Person.PersonType.COUNCIL_MEMBER,
    )
    person.council_member = CouncilMember(
        city_council_person_id=city_council_person_id
    )
    db.session.add(person)
    return person


def add_test_sponsorship(*, bill, person):
    sequence = 0

    def impl():
        nonlocal sequence
        sponsorship = CitySponsorship(
            bill_id=bill.id,
            council_member_id=person.id,
            sponsor_sequence=sequence,
        )
        db.session.add(sponsorship)
        sequence += 1
        return sponsorship

    return impl()


def test_calculate_all_bill_diffs__city():
    bill_1 = add_test_bill(1, "Enacted")
    bill_2 = add_test_bill(2, "Enacted")
    council_member_1 = add_test_council_member(1)
    council_member_2 = add_test_council_member(2)
    council_member_3 = add_test_council_member(3)
    add_test_sponsorship(bill=bill_1, person=council_member_1)
    add_test_sponsorship(bill=bill_1, person=council_member_3)
    add_test_sponsorship(bill=bill_2, person=council_member_3)

    db.session.commit()

    snapshots = {
        # This should change status, lose sponsor 2 and gain sponsor 3
        bill_1.id: GenericBillSnapshot(
            status="Committee", sponsor_person_ids={council_member_1.id, council_member_2.id}
        ),
        # This should be unchanged
        bill_2.id: GenericBillSnapshot(status="Enacted", sponsor_person_ids={council_member_3.id}),
    }
    diffs = _calculate_all_bill_diffs(SnapshotState(city_snapshots=snapshots, state_snapshots={}))

    assert len(diffs.city_diffs) == 1
    diff = diffs.city_diffs[0]

    assert diff.added_sponsor_names == [council_member_3.name]
    assert diff.removed_sponsor_names == [council_member_2.name]
    assert diff.old_status == "Committee"
    assert diff.new_status == "Enacted"


def test_calculate_all_bill_diffs__state():
    pass


def test_email_contents__status_changed():
    bill = add_test_bill(1, "Enacted")
    diff = GenericBillDiff(
        old_status="Committee",
        new_status="Enacted",
        added_sponsor_names=[],
        removed_sponsor_names=[],
        current_sponsor_count=0,
        bill_number=bill.code_name,
        bill_name=bill.display_name
    )

    subject = _get_bill_update_subject_line(BillDiffSet(state_diffs=[], city_diffs=[diff]))
    assert subject == f"City bill {bill.code_name}'s status changed to Enacted"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "bill_number": bill.code_name,
        "bill_name": bill.display_name,
        "status_text": "Status: Committee --> Enacted",
        "status_color": "blue",
        "sponsor_text": "0 sponsors (unchanged)",
        "sponsor_color": "black",
    }


def test_email_contents__sponsors_added():
    bill = add_test_bill(1, "Enacted")
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        added_sponsor_names=["Brad Lander", "Jamaal Bowman"],
        removed_sponsor_names=[],
        current_sponsor_count=3,
        bill_number=bill.code_name,
        bill_name=bill.display_name
    )

    # It uses the current sponsor count to figure out the previous, so
    # add some sponsors in the DB so it doesn't report a negative number
    for i in range(3):
        person = add_test_council_member(i)
        add_test_sponsorship(bill=bill, person=person)

    db.session.commit()

    subject = _get_bill_update_subject_line(BillDiffSet(state_diffs=[], city_diffs=[diff]))
    assert subject == f"City bill {bill.code_name} gained 2 sponsors"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "bill_number": bill.code_name,
        "bill_name": bill.display_name,
        "status_text": "Status: Enacted (unchanged)",
        "status_color": "black",
        "sponsor_text": "1 sponsors --> 3 sponsors (gained Brad Lander, Jamaal Bowman)",
        "sponsor_color": "blue",
    }


def test_email_subject__1_sponsor_added():
    bill = add_test_bill(1, "Enacted")
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        added_sponsor_names=["Brad Lander"],
        removed_sponsor_names=[],
        current_sponsor_count=3,
        bill_number=bill.code_name,
        bill_name=bill.display_name
    )

    for i in range(3):
        person = add_test_council_member(i)
        add_test_sponsorship(bill=bill, person=person)

    db.session.commit()

    subject = _get_bill_update_subject_line(BillDiffSet(state_diffs=[], city_diffs=[diff]))
    assert subject == f"City bill {bill.code_name} gained sponsor Brad Lander"


def test_email_contents__sponsor_removed():
    bill = add_test_bill(1, "Enacted")
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        removed_sponsor_names=["Brad Lander"],
        added_sponsor_names=[],
        current_sponsor_count=0,
        bill_number=bill.code_name,
        bill_name=bill.display_name
    )

    subject = _get_bill_update_subject_line(BillDiffSet(state_diffs=[], city_diffs=[diff]))
    assert subject == f"City bill {bill.code_name} lost sponsor Brad Lander"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "bill_number": bill.code_name,
        "bill_name": bill.display_name,
        "status_text": "Status: Enacted (unchanged)",
        "status_color": "black",
        "sponsor_text": "1 sponsors --> 0 sponsors (lost Brad Lander)",
        "sponsor_color": "blue",
    }


def test_email_contents__sponsor_added_and_removed():
    bill = add_test_bill(1, "Enacted")
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        removed_sponsor_names=["Brad Lander"],
        added_sponsor_names=["Jamaal Bowman"],
        current_sponsor_count=1,
        bill_number=bill.code_name,
        bill_name=bill.display_name
    )

    person = add_test_council_member(1)
    add_test_sponsorship(bill=bill, person=person)

    db.session.commit()

    subject = _get_bill_update_subject_line(BillDiffSet(state_diffs=[], city_diffs=[diff]))
    assert subject == f"City bill {bill.code_name} gained and lost sponsors"

    variables = _convert_bill_diff_to_template_variables(diff)
    assert variables == {
        "bill_number": bill.code_name,
        "bill_name": bill.display_name,
        "status_text": "Status: Enacted (unchanged)",
        "status_color": "black",
        "sponsor_text": "1 sponsors --> 1 sponsors (gained Jamaal Bowman, lost Brad Lander)",
        "sponsor_color": "blue",
    }


# TODO: Test a few state email subject lines stoo!


@responses.activate
@patch("src.ses.client")
def test_state_bill_ignored(mock_ses_client):
    bill = Bill(
        id=uuid4(),
        name="state bill",
        description="description",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.senate_bill = SenateBill(
        base_print_no="S1234", active_version="A", status="Signed by governor"
    )
    bill.state_bill.assembly_bill = AssemblyBill(
        base_print_no="A1234", active_version="", status="Signed by governor"
    )
    db.session.add(bill)
    db.session.commit()

    snapshots = {}

    with app.app_context():
        send_bill_update_notifications(snapshots)

    mock_ses_client.send_email.assert_not_called()


@responses.activate
@patch("src.ses.client")
def test_send_email_notification_end_to_end(mock_ses_client):
    user_to_notify = User(
        id=uuid4(),
        name="User to notify",
        email="user@example.com",
        send_bill_update_notifications=True,
    )
    db.session.add(user_to_notify)
    other_user = User(
        id=uuid4(), name="Someone else", email="wrong@example.com"
    )
    db.session.add(other_user)

    bill = add_test_bill(1, "Enacted")

    db.session.commit()

    snapshots = {
        bill.id: GenericBillSnapshot("Committee", sponsor_ids=[]),
    }

    def side_effect(*, Destination, Message, Source):
        assert Destination["ToAddresses"] == ["user@example.com"]
        assert "Enacted" in Message["Body"]["Html"]["Data"]
        assert "Enacted" in Message["Body"]["Text"]["Data"]
        assert "Enacted" in Message["Subject"]["Data"]
        return {"MessageId": 1}

    mock_ses_client.send_email.side_effect = side_effect

    with app.app_context():
        send_bill_update_notifications(snapshots)

    mock_ses_client.send_email.assert_called_once()
