from unittest.mock import patch
from uuid import uuid4

import pytest
import responses

from src.app import app
from src.bill.models import (
    AssemblyBill,
    Bill,
    CityBill,
    SenateBill,
    StateBill,
    UserBillSettings,
)
from src.bill_notifications import (
    BillDiffSet,
    GenericBillDiff,
    GenericBillSnapshot,
    SnapshotState,
    StateBillDiff,
    StateBillSnapshot,
    _calculate_all_bill_diffs,
    _filter_diffs_for_user,
    _render_email_contents,
    send_bill_update_notifications,
)
from src.models import db
from src.person.models import AssemblyMember, CouncilMember, Person, Senator
from src.sponsorship.models import (
    AssemblySponsorship,
    CitySponsorship,
    SenateSponsorship,
)
from src.user.models import User
from src.utils import now


def make_email_snapshot(subject, body_html, body_text):
    """Puts all parts of an email into a single string that's convenient
    for snapshot tests."""

    return f"""
SUBJECT--------------------------------------------
{subject}

BODY HTML------------------------------------------
{body_html}

BODY TEXT-------------------------------------------
{body_text}"""


# TODO: Switch to Factory
def add_test_city_bill(city_bill_id, status):
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
    bill_1 = add_test_city_bill(1, "Enacted")
    bill_2 = add_test_city_bill(2, "Enacted")
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
            status="Committee",
            sponsor_person_ids={council_member_1.id, council_member_2.id},
        ),
        # This should be unchanged
        bill_2.id: GenericBillSnapshot(
            status="Enacted", sponsor_person_ids={council_member_3.id}
        ),
    }
    diffs = _calculate_all_bill_diffs(
        SnapshotState(city_snapshots=snapshots, state_snapshots={})
    )

    assert len(diffs.city_diffs) == 1
    diff = diffs.city_diffs[0]

    assert diff.added_sponsor_names == [council_member_3.name]
    assert diff.removed_sponsor_names == [council_member_2.name]
    assert diff.old_status == "Committee"
    assert diff.new_status == "Enacted"


def test_calculate_all_bill_diffs__state_senate(get_uuid, senator):
    bill = Bill(
        id=get_uuid(),
        name="state bill",
        description="ban oil",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.senate_bill = SenateBill(
        base_print_no="S1234", active_version="", status="Signed by governor"
    )
    db.session.add(bill)

    old_senator = Person(
        id=get_uuid(), name="removed sponsor", type=Person.PersonType.SENATOR
    )
    old_senator.senator = Senator(state_member_id=500)
    db.session.add(old_senator)

    new_senator = Person(
        id=get_uuid(), name="added sponsor", type=Person.PersonType.SENATOR
    )
    new_senator.senator = Senator(state_member_id=100)
    new_senator.senator.sponsorships.append(
        SenateSponsorship(bill_id=bill.id, is_lead_sponsor=False)
    )

    senator.senator.sponsorships.append(
        SenateSponsorship(bill_id=bill.id, is_lead_sponsor=False)
    )
    db.session.add(new_senator)

    db.session.commit()

    snapshots = {
        # This should change status, lose old_senator, and gain new_senator, while keeping senator
        bill.id: StateBillSnapshot(
            senate_snapshot=GenericBillSnapshot(
                status="Committee",
                sponsor_person_ids={senator.id, old_senator.id},
            )
        )
    }
    diffs = _calculate_all_bill_diffs(
        SnapshotState(city_snapshots={}, state_snapshots=snapshots)
    )

    assert len(diffs.state_diffs) == 1
    assert not diffs.state_diffs[0].assembly_diff
    diff = diffs.state_diffs[0].senate_diff

    assert diff.added_sponsor_names == [new_senator.name]
    assert diff.removed_sponsor_names == [old_senator.name]
    assert diff.old_status == "Committee"
    assert diff.new_status == "Signed by governor"


def test_calculate_all_bill_diffs__state_assembly(get_uuid, assembly_member):
    bill = Bill(
        id=get_uuid(),
        name="state bill",
        description="ban oil",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.assembly_bill = AssemblyBill(
        base_print_no="A1234", active_version="", status="Signed by governor"
    )
    db.session.add(bill)

    old_assembly_member = Person(
        id=get_uuid(),
        name="removed sponsor",
        type=Person.PersonType.ASSEMBLY_MEMBER,
    )
    old_assembly_member.assembly_member = AssemblyMember(state_member_id=500)
    db.session.add(old_assembly_member)

    new_assembly_member = Person(
        id=get_uuid(),
        name="added sponsor",
        type=Person.PersonType.ASSEMBLY_MEMBER,
    )
    new_assembly_member.assembly_member = AssemblyMember(state_member_id=100)
    new_assembly_member.assembly_member.sponsorships.append(
        AssemblySponsorship(bill_id=bill.id, is_lead_sponsor=False)
    )

    assembly_member.assembly_member.sponsorships.append(
        AssemblySponsorship(bill_id=bill.id, is_lead_sponsor=False)
    )
    db.session.add(new_assembly_member)

    db.session.commit()

    snapshots = {
        # This should change status, lose old_assembly_member, and gain new_assembly_member, while keeping assembly_member
        bill.id: StateBillSnapshot(
            assembly_snapshot=GenericBillSnapshot(
                status="Committee",
                sponsor_person_ids={
                    assembly_member.id,
                    old_assembly_member.id,
                },
            )
        )
    }
    diffs = _calculate_all_bill_diffs(
        SnapshotState(city_snapshots={}, state_snapshots=snapshots)
    )

    assert len(diffs.state_diffs) == 1
    assert not diffs.state_diffs[0].senate_diff
    diff = diffs.state_diffs[0].assembly_diff

    assert diff.added_sponsor_names == [new_assembly_member.name]
    assert diff.removed_sponsor_names == [old_assembly_member.name]
    assert diff.old_status == "Committee"
    assert diff.new_status == "Signed by governor"


def test_calculate_all_bill_diffs__state_unchanged(get_uuid):
    bill = Bill(
        id=get_uuid(),
        name="state bill",
        description="ban oil",
        type=Bill.BillType.STATE,
    )
    bill.state_bill = StateBill(
        session_year=2021,
    )
    bill.state_bill.senate_bill = SenateBill(
        base_print_no="S1234", active_version="", status="Committee"
    )
    db.session.add(bill)
    db.session.commit()

    snapshots = {
        bill.id: StateBillSnapshot(
            senate_snapshot=GenericBillSnapshot(
                status="Committee", sponsor_person_ids=set()
            )
        )
    }
    diffs = _calculate_all_bill_diffs(
        SnapshotState(city_snapshots={}, state_snapshots=snapshots)
    )

    assert len(diffs.state_diffs) == 0
    assert len(diffs.city_diffs) == 0


def test_email_contents__city_status_changed(snapshot):
    diff = GenericBillDiff(
        old_status="Committee",
        new_status="Enacted",
        added_sponsor_names=[],
        removed_sponsor_names=[],
        current_sponsor_count=0,
        bill_number="Intro 2317",
        bill_name="Gas Free NYC",
    )

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(state_diffs=[], city_diffs=[diff])
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__state_status_changed(snapshot):
    senate_diff = GenericBillDiff(
        old_status="Committee",
        new_status="Signed by governor",
        added_sponsor_names=[],
        removed_sponsor_names=[],
        current_sponsor_count=0,
        bill_number="S4264",
        bill_name="CCIA",
    )

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(
                state_diffs=[
                    StateBillDiff(senate_diff=senate_diff, assembly_diff=None)
                ],
                city_diffs=[],
            )
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__state_both_status_changed(snapshot):
    senate_diff = GenericBillDiff(
        old_status="Committee",
        new_status="Signed by governor",
        added_sponsor_names=[],
        removed_sponsor_names=[],
        current_sponsor_count=0,
        bill_number="S4264",
        bill_name="CCIA",
    )
    assembly_diff = GenericBillDiff(
        old_status="Committee",
        new_status="Signed by governor",
        added_sponsor_names=[],
        removed_sponsor_names=[],
        current_sponsor_count=0,
        bill_number="A4264",
        bill_name="CCIA",
    )

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(
                state_diffs=[
                    StateBillDiff(
                        senate_diff=senate_diff, assembly_diff=assembly_diff
                    )
                ],
                city_diffs=[],
            )
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__state_gained_senate_sponsor(snapshot):
    senate_diff = GenericBillDiff(
        old_status="Committee",
        new_status="Committee",
        added_sponsor_names=["Jabari Brisport"],
        removed_sponsor_names=[],
        current_sponsor_count=1,
        bill_number="S4264",
        bill_name="CCIA",
    )

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(
                state_diffs=[
                    StateBillDiff(senate_diff=senate_diff, assembly_diff=None)
                ],
                city_diffs=[],
            )
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__state_lost_assembly_sponsor(snapshot):
    assembly_diff = GenericBillDiff(
        old_status="Committee",
        new_status="Committee",
        added_sponsor_names=[],
        removed_sponsor_names=["Emily Gallagher"],
        current_sponsor_count=0,
        bill_number="A234",
        bill_name="CCIA",
    )

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(
                state_diffs=[
                    StateBillDiff(
                        senate_diff=None, assembly_diff=assembly_diff
                    )
                ],
                city_diffs=[],
            )
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__city_sponsors_added(snapshot):
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        added_sponsor_names=["Brad Lander", "Jamaal Bowman"],
        removed_sponsor_names=[],
        current_sponsor_count=3,
        bill_number="Intro 2317",
        bill_name="Gass Free NYC",
    )

    db.session.commit()

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(state_diffs=[], city_diffs=[diff])
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_subject__1_city_sponsor_added(snapshot):
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        added_sponsor_names=["Brad Lander"],
        removed_sponsor_names=[],
        current_sponsor_count=3,
        bill_number="Intro 2317",
        bill_name="Gas Free NYC",
    )

    db.session.commit()

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(state_diffs=[], city_diffs=[diff])
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__city_sponsor_removed(snapshot):
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        removed_sponsor_names=["Brad Lander"],
        added_sponsor_names=[],
        current_sponsor_count=0,
        bill_number="Intro 2317",
        bill_name="Gas Free NYC",
    )

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(state_diffs=[], city_diffs=[diff])
        )

    assert snapshot == make_email_snapshot(subject, html, text)


def test_email_contents__city_sponsor_added_and_removed(snapshot):
    diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        removed_sponsor_names=["Brad Lander"],
        added_sponsor_names=["Jamaal Bowman"],
        current_sponsor_count=1,
        bill_number="Intro 2317",
        bill_name="Gass Free NYC",
    )

    db.session.commit()

    with app.app_context():
        subject, html, text = _render_email_contents(
            BillDiffSet(state_diffs=[], city_diffs=[diff])
        )

    assert snapshot == make_email_snapshot(subject, html, text)


@pytest.mark.parametrize(
    ("notify", "expected_diff_count"), [(False, 0), (True, 1)]
)
def test_filter_diffs_for_user(
    user, state_bill, city_bill, notify, expected_diff_count
):
    user.bill_settings.append(
        UserBillSettings(
            bill_id=state_bill.id, send_bill_update_notifications=notify
        )
    )
    user.bill_settings.append(
        UserBillSettings(
            bill_id=city_bill.id, send_bill_update_notifications=notify
        )
    )
    db.session.commit()

    city_diff = GenericBillDiff(
        old_status="Enacted",
        new_status="Enacted",
        removed_sponsor_names=["Brad Lander"],
        added_sponsor_names=["Jamaal Bowman"],
        current_sponsor_count=1,
        bill_number="Intro 2317",
        bill_name="Gas Free NYC",
        bill_id=city_bill.id,
    )

    state_diff = StateBillDiff(
        bill_id=state_bill.id,
        senate_diff=GenericBillDiff(
            old_status="Signed by Governor",
            new_status="Unknown",
            removed_sponsor_names=[],
            added_sponsor_names=[],
            current_sponsor_count=1,
            bill_number="S123",
            bill_name="Bill to include",
            bill_id=state_bill.id,
        ),
    )
    diff_set = BillDiffSet(state_diffs=[state_diff], city_diffs=[city_diff])

    filtered_diff_set = _filter_diffs_for_user(user, diff_set)
    assert len(filtered_diff_set.city_diffs) == expected_diff_count
    assert len(filtered_diff_set.state_diffs) == expected_diff_count


@responses.activate
@patch("src.ses.client")
def test_send_email_notification_end_to_end(
    mock_ses_client, city_bill, state_bill, snapshot
):
    user_to_notify = User(
        id=uuid4(),
        name="User to notify",
        email="user@example.com",
    )
    user_to_notify.bill_settings.append(
        UserBillSettings(
            bill_id=city_bill.id, send_bill_update_notifications=True
        )
    )
    user_to_notify.bill_settings.append(
        UserBillSettings(
            bill_id=state_bill.id, send_bill_update_notifications=True
        )
    )
    db.session.add(user_to_notify)
    other_user = User(
        id=uuid4(), name="Someone else", email="wrong@example.com"
    )
    db.session.add(other_user)

    db.session.commit()

    snapshot_state = SnapshotState(
        city_snapshots={
            city_bill.id: GenericBillSnapshot(
                "Not introduced", sponsor_person_ids=set()
            ),
        },
        state_snapshots={
            state_bill.id: StateBillSnapshot(
                senate_snapshot=GenericBillSnapshot(
                    "Introduced in senate", sponsor_person_ids=set()
                ),
                assembly_snapshot=GenericBillSnapshot(
                    "Introduced in assembly", sponsor_person_ids=set()
                ),
            )
        },
    )

    def side_effect(*, Destination, Message, Source):
        assert Destination["ToAddresses"] == ["user@example.com"]
        assert snapshot == make_email_snapshot(
            Message["Subject"]["Data"],
            Message["Body"]["Html"]["Data"],
            Message["Body"]["Text"]["Data"],
        )

        return {"MessageId": 1}

    mock_ses_client.send_email.side_effect = side_effect

    with app.app_context():
        send_bill_update_notifications(snapshot_state)

    mock_ses_client.send_email.assert_called_once()
