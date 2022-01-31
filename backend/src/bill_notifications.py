import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Union
from uuid import UUID
from collections import defaultdict

from botocore.exceptions import ClientError
from flask import render_template

from .bill.models import AssemblyBill, Bill, SenateBill, UserBillSettings
from .person.models import Person
from .ses import send_email
from .user.models import User


@dataclass
class GenericBillDiff:
    """Utility class to track a bill's state before and after a cron run. Applies to
    a city bill or a single chamber of a state bill."""

    old_status: str = None
    new_status: str = None

    added_sponsor_names: List[str] = None
    removed_sponsor_names: List[str] = None
    current_sponsor_count: int = None

    bill_number: str = None
    bill_name: str = None
    bill_id: UUID = None # need to fill this


@dataclass
class StateBillDiff:
    bill_id: UUID = None # need to fill
    senate_diff: Optional[GenericBillDiff] = None
    assembly_diff: Optional[GenericBillDiff] = None


@dataclass
class BillDiffSet:
    state_diffs: List[StateBillDiff] = None
    city_diffs: List[GenericBillDiff] = None


@dataclass
class GenericBillSnapshot:
    """Utility class to track the state of a bill before a cron run may have
    updated it. Applies to a city bill or a single chamber of a state bill."""

    status: str = None
    sponsor_person_ids: Set[UUID] = None


@dataclass
class StateBillSnapshot:
    # These are None if the bill does not exist in that chamber
    senate_snapshot: Optional[GenericBillSnapshot] = None
    assembly_snapshot: Optional[GenericBillSnapshot] = None


@dataclass
class SnapshotState:
    city_snapshots: Dict[UUID, GenericBillSnapshot] = None
    state_snapshots: Dict[UUID, StateBillSnapshot] = None


def _snapshot_state_bill_chamber(
    chamber_bill: Optional[Union[SenateBill, AssemblyBill]]
) -> Optional[GenericBillSnapshot]:
    if not chamber_bill:
        return None

    sponsor_ids = set((s.person_id for s in chamber_bill.sponsorships))
    status = chamber_bill.status

    return GenericBillSnapshot(status=status, sponsor_person_ids=sponsor_ids)


def snapshot_bills() -> SnapshotState:
    """Snapshots the state of all bills. Used to calculate the diff produced by
    a cron job run, so that we can send out email notifications of bill status changes."""

    snapshot_state = SnapshotState(city_snapshots={}, state_snapshots={})

    # FIXME: This is doing a lot of lazy loading of sponsorships
    bills = Bill.query.all()
    for bill in bills:
        if bill.type == Bill.BillType.CITY:
            sponsor_ids = set(
                (s.council_member_id for s in bill.city_bill.sponsorships)
            )
            snapshot = GenericBillSnapshot(bill.city_bill.status, sponsor_ids)
            snapshot_state.city_snapshots[bill.id] = snapshot
        else:
            snapshot_state.state_snapshots[bill.id] = StateBillSnapshot(
                senate_snapshot=_snapshot_state_bill_chamber(
                    bill.state_bill.senate_bill
                ),
                assembly_snapshot=_snapshot_state_bill_chamber(
                    bill.state_bill.assembly_bill
                ),
            )

    return snapshot_state


def _get_sponsor_subject_string(sponsors):
    if len(sponsors) > 1:
        return f"{len(sponsors)} sponsors"

    return f"sponsor {sponsors[0]}"


def _get_bill_update_subject_line(bill_diffs: BillDiffSet):
    """Get a subject line for the email describing the bill updates. Assumes the diff list
    and the diffs themselves are non-empty."""
    total_bill_diffs = len(bill_diffs.city_diffs) + len(bill_diffs.state_diffs)
    if total_bill_diffs > 1:
        return f"{total_bill_diffs} bills were updated"

    if bill_diffs.city_diffs:
        diff = bill_diffs.city_diffs[0]
        bill_description = f"City bill {diff.bill_number}"
    else:
        state_diff = bill_diffs.state_diffs[0]

        if state_diff.assembly_diff and state_diff.senate_diff:
            return f"State bill {state_diff.assembly_diff.bill_number}/{state_diff.senate_diff.bill_number} was updated in both chambers"

        diff = state_diff.senate_diff or state_diff.assembly_diff
        bill_description = f"State bill {diff.bill_number}"

    # TODO: Update to python 3.10 and use structural pattern matching?
    if not diff.added_sponsor_names and not diff.removed_sponsor_names:
        return f"{bill_description}'s status changed to {diff.new_status}"

    if diff.old_status == diff.new_status:
        if not diff.added_sponsor_names:
            return f"{bill_description} lost {_get_sponsor_subject_string(diff.removed_sponsor_names)}"
        if not diff.removed_sponsor_names:
            return f"{bill_description} gained {_get_sponsor_subject_string(diff.added_sponsor_names)}"
        return f"{bill_description} gained and lost sponsors"

    return f"{bill_description} was updated"


def _convert_bill_diff_to_template_variables(diff: GenericBillDiff):
    """Converts the intermediate BillDiff into the variables used to render
    the email template."""
    status_changed = diff.new_status != diff.old_status
    if status_changed:
        status_text = f"Status: {diff.old_status} --> {diff.new_status}"
        status_color = "blue"
    else:
        status_text = f"Status: {diff.new_status} (unchanged)"
        status_color = "black"

    sponsors_changed = diff.added_sponsor_names or diff.removed_sponsor_names
    if sponsors_changed:
        old_sponsor_count = (
            diff.current_sponsor_count
            - len(diff.added_sponsor_names or [])
            + len(diff.removed_sponsor_names or [])
        )
        sponsor_color = "blue"

        # List out the names of all changed sponsors
        explanations = []
        if diff.added_sponsor_names:
            explanations.append(
                f"gained {', '.join(diff.added_sponsor_names)}"
            )
        if diff.removed_sponsor_names:
            explanations.append(
                f"lost {', '.join(diff.removed_sponsor_names)}"
            )

        sponsor_text = f"{old_sponsor_count} sponsors --> {diff.current_sponsor_count} sponsors ({', '.join(explanations)})"
    else:
        sponsor_text = f"{diff.current_sponsor_count} sponsors (unchanged)"
        sponsor_color = "black"

    return {
        "bill_number": diff.bill_number,
        "bill_name": diff.bill_name,
        "status_text": status_text,
        "status_color": status_color,
        "sponsor_text": sponsor_text,
        "sponsor_color": sponsor_color,
    }


def _get_diff_set_template_variables(bill_diffs: BillDiffSet):
    city_bills_for_template = []
    for city_diff in bill_diffs.city_diffs:
        city_bills_for_template.append(
            _convert_bill_diff_to_template_variables(city_diff)
        )
    state_bills_for_template = []
    for state_diff in bill_diffs.state_diffs:
        chamber_bills = []
        if state_diff.senate_diff:
            chamber_bills.append(
                {
                    "chamber_name": "Senate",
                    **_convert_bill_diff_to_template_variables(
                        state_diff.senate_diff
                    ),
                }
            )
        if state_diff.assembly_diff:
            chamber_bills.append(
                {
                    "chamber_name": "Assembly",
                    **_convert_bill_diff_to_template_variables(
                        state_diff.assembly_diff
                    ),
                }
            )
        state_bills_for_template.append({"chamber_bills": chamber_bills})
    return {
        "city_bills": city_bills_for_template,
        "state_bills": state_bills_for_template,
    }


def _render_email_contents(bill_diffs: BillDiffSet):
    template_variables = _get_diff_set_template_variables(bill_diffs)
    subject = _get_bill_update_subject_line(bill_diffs)
    body_text = render_template(
        "bill_alerts_email.txt",
        **template_variables,
    )
    body_html = render_template(
        "bill_alerts_email.html",
        **template_variables,
    )
    return subject, body_html, body_text


def _calculate_bill_diff(
    *,
    snapshot: GenericBillSnapshot,
    current_sponsor_ids: Set[UUID],
    new_status,
    bill_number: str,
    bill_name: Optional[str],
) -> Optional[GenericBillDiff]:
    """Looks at the before and after states of a single bill and computes a diff
    that's useful for sending email notifications."""

    added_sponsor_ids = current_sponsor_ids - snapshot.sponsor_person_ids
    removed_sponsor_ids = snapshot.sponsor_person_ids - current_sponsor_ids

    changed_persons = Person.query.filter(
        Person.id.in_(added_sponsor_ids.union(removed_sponsor_ids))
    ).all()
    added_sponsor_names = [
        p.name for p in changed_persons if p.id in added_sponsor_ids
    ]
    removed_sponsor_names = [
        p.name for p in changed_persons if p.id in removed_sponsor_ids
    ]

    if (
        removed_sponsor_names
        or added_sponsor_names
        or new_status != snapshot.status
    ):
        return GenericBillDiff(
            old_status=snapshot.status,
            new_status=new_status,
            added_sponsor_names=added_sponsor_names,
            removed_sponsor_names=removed_sponsor_names,
            current_sponsor_count=len(current_sponsor_ids),
            bill_number=bill_number,
            bill_name=bill_name,
        )

    return None


def _calculate_all_bill_diffs(snapshot_state: SnapshotState) -> BillDiffSet:
    """
    Compares the current state of all tracked bills with a snapshot of their recent
    previous state, and creates a diff that describes the important information needed
    to send an email notification about any changes.
    """
    bills = Bill.query.all()

    bill_diffs = BillDiffSet(state_diffs=[], city_diffs=[])
    for bill in bills:
        if bill.type == Bill.BillType.CITY:
            snapshot = snapshot_state.city_snapshots[bill.id]
            current_sponsor_ids = set(
                (s.council_member_id for s in bill.city_bill.sponsorships)
            )
            diff = _calculate_bill_diff(
                snapshot=snapshot,
                current_sponsor_ids=current_sponsor_ids,
                new_status=bill.city_bill.status,
                bill_number=bill.city_bill.file,
                bill_name=bill.display_name,
            )
            if diff:
                bill_diffs.city_diffs.append(diff)
        else:
            snapshot = snapshot_state.state_snapshots[bill.id]
            if bill.state_bill.senate_bill:
                senate_diff = _calculate_bill_diff(
                    snapshot=snapshot.senate_snapshot,
                    current_sponsor_ids=set(
                        (
                            s.person_id
                            for s in bill.state_bill.senate_bill.sponsorships
                        )
                    ),
                    new_status=bill.state_bill.senate_bill.status,
                    bill_number=bill.state_bill.senate_bill.base_print_no,
                    bill_name=bill.display_name,
                )
            else:
                senate_diff = None

            if bill.state_bill.assembly_bill:
                assembly_diff = _calculate_bill_diff(
                    snapshot=snapshot.assembly_snapshot,
                    current_sponsor_ids=set(
                        (
                            s.person_id
                            for s in bill.state_bill.assembly_bill.sponsorships
                        )
                    ),
                    new_status=bill.state_bill.assembly_bill.status,
                    bill_number=bill.state_bill.assembly_bill.base_print_no,
                    bill_name=bill.display_name,
                )
            else:
                assembly_diff = None

            if senate_diff or assembly_diff:
                bill_diffs.state_diffs.append(
                    StateBillDiff(
                        senate_diff=senate_diff, assembly_diff=assembly_diff
                    )
                )

    return bill_diffs


def _create_filtered_bill_diffs(full_diffs: BillDiffSet, bill_ids: Set[UUID]) -> BillDiffSet:
    filtered_diffs = BillDiffSet()
    filtered_diffs.state_diffs = [d for d in full_diffs.state_diffs if d.bill_id in bill_ids]
    filtered_diffs.city_diffs = [d for d in full_diffs.city_diffs if d.bill_id in bill_ids]
    return filtered_diffs


def send_bill_update_notifications(
    snapshots_by_bill_id,
):
    bill_diffs = _calculate_all_bill_diffs(snapshots_by_bill_id)

    if bill_diffs.city_diffs or bill_diffs.state_diffs:
        logging.info("Bills were changed in this cron run, sending emails")

        changed_bill_ids = [d.bill_id for d in bill_diffs.city_diffs] + [d.bill_id for d in bill_diffs.state_diffs]
        relevant_notification_settings = UserBillSettings.query.filter(
            UserBillSettings.send_bill_update_notifications==True,
            UserBillSettings.bill_id.in_(changed_bill_ids)
        ).all()

        bill_settings_by_user_id = defaultdict(lambda: set())
        for setting in relevant_notification_settings:
            bill_settings_by_user_id[setting.user_id].add(setting)

        # Maybe split out separate function?
        for bill_settings in bill_settings_by_user_id.values():
            requested_bill_ids = [s.bill_id for s in bill_settings]
            filtered_diffs_for_user = _create_filtered_bill_diffs(bill_diffs, requested_bill_ids)
            user = bill_settings[0].user

            subject, body_html, body_text = _render_email_contents(filtered_diffs_for_user)

            logging.info(f"Sending bill update email to {user.email}")
            try:
                send_email(user.email, subject, body_html, body_text)
            except ClientError:
                logging.exception(f"Failed to send email to {user.email}")
