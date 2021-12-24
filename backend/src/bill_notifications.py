import logging
from dataclasses import dataclass
from typing import List

from botocore.exceptions import ClientError
from flask import render_template
from sqlalchemy.orm import selectinload

from .bill.views import Bill
from .person.models import Legislator
from .ses import send_email
from .user.models import User


@dataclass
class BillDiff:
    """Utility class to track a bill's state before and after a cron run."""

    bill: Bill = None
    old_status: str = None
    added_sponsor_names: List[str] = None
    removed_sponsor_names: List[str] = None


@dataclass
class BillSnapshot:
    """Utility class to track the state of a bill before a cron run may have
    updated it."""

    status: str = None
    sponsor_ids: List[int] = None


def snapshot_bills():
    """Snapshots the state of all bills. Used to calculate the diff produced by
    a cron job run, so that we can send out email notifications of bill status changes."""
    bills = Bill.query.options(selectinload(Bill.sponsorships)).all()

    snapshots_by_bill_id = {}
    for bill in bills:
        sponsor_ids = [s.legislator_id for s in bill.sponsorships]
        snapshot = BillSnapshot(bill.status, sponsor_ids)
        snapshots_by_bill_id[bill.id] = snapshot

    return snapshots_by_bill_id


def _get_sponsor_subject_string(sponsors):
    if len(sponsors) > 1:
        return f"{len(sponsors)} sponsors"

    return f"sponsor {sponsors[0]}"


def _get_bill_update_subject_line(bill_diffs):
    """Get a subject line for the email describing the bill updates. Assumes the diff list
    and the diffs themselves are non-empty."""
    if len(bill_diffs) > 1:
        return f"{len(bill_diffs)} bills were updated"

    diff = bill_diffs[0]

    # TODO: Update to python 3.10 and use structural pattern matching?
    file = diff.bill.file
    if not diff.added_sponsor_names and not diff.removed_sponsor_names:
        return f"{file}'s status changed to {diff.bill.status}"

    if diff.old_status == diff.bill.status:
        if not diff.added_sponsor_names:
            return f"{file} lost {_get_sponsor_subject_string(diff.removed_sponsor_names)}"
        if not diff.removed_sponsor_names:
            return f"{file} gained {_get_sponsor_subject_string(diff.added_sponsor_names)}"
        return f"{file} gained and lost sponsors"

    return f"{diff.bill.file} was updated"


def _convert_bill_diff_to_template_variables(diff):
    """Converts the intermediate BillDiff into the variables used to render
    the email template."""
    status_changed = diff.bill.status != diff.old_status
    if status_changed:
        status_text = f"Status: {diff.old_status} --> {diff.bill.status}"
        status_color = "blue"
    else:
        status_text = f"Status: {diff.bill.status} (unchanged)"
        status_color = "black"

    sponsors_changed = diff.added_sponsor_names or diff.removed_sponsor_names
    if sponsors_changed:
        new_sponsor_count = len(diff.bill.sponsorships)
        old_sponsor_count = (
            new_sponsor_count
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

        sponsor_text = f"{old_sponsor_count} sponsors --> {new_sponsor_count} sponsors ({', '.join(explanations)})"
    else:
        sponsor_text = f"{len(diff.bill.sponsorships)} sponsors (unchanged)"
        sponsor_color = "black"

    return {
        "file": diff.bill.file,
        "display_name": diff.bill.display_name,
        "status_text": status_text,
        "status_color": status_color,
        "sponsor_text": sponsor_text,
        "sponsor_color": sponsor_color,
    }


def _send_bill_update_emails(bill_diffs):
    bills_for_template = [
        _convert_bill_diff_to_template_variables(d) for d in bill_diffs
    ]

    subject = _get_bill_update_subject_line(bill_diffs)
    body_text = render_template(
        "bill_alerts_email.txt", bills=bills_for_template
    )
    body_html = render_template(
        "bill_alerts_email.html", bills=bills_for_template
    )

    users_to_notify = User.query.filter_by(
        send_bill_update_notifications=True
    ).all()

    for user in users_to_notify:
        logging.info(f"Sending bill update email to {user.email}")
        try:
            send_email(user.email, subject, body_html, body_text)
        except ClientError:
            logging.exception(f"Faild to send email to {user.email}")


def _calculate_bill_diffs(snapshots_by_bill_id):
    """Looks at the before and after states of all bills, and collapses this info
    info a form that's useful for further processing when building emails."""
    bills = Bill.query.options(selectinload("sponsorships.legislator")).all()

    bill_diffs = []
    for bill in bills:
        snapshot = snapshots_by_bill_id[bill.id]

        added_sponsors = []
        prior_sponsor_ids = set(snapshot.sponsor_ids)
        for sponsorship in bill.sponsorships:
            if sponsorship.legislator_id not in prior_sponsor_ids:
                added_sponsors.append(sponsorship.legislator)
            else:
                prior_sponsor_ids.remove(sponsorship.legislator_id)

        if prior_sponsor_ids:
            removed_sponsors = Legislator.query.filter(
                Legislator.id.in_(prior_sponsor_ids)
            ).all()
        else:
            removed_sponsors = []

        if (
            removed_sponsors
            or added_sponsors
            or bill.status != snapshot.status
        ):
            diff = BillDiff()
            diff.bill = bill
            diff.old_status = snapshot.status
            diff.added_sponsor_names = [s.name for s in added_sponsors]
            diff.removed_sponsor_names = [s.name for s in removed_sponsors]
            bill_diffs.append(diff)

    return bill_diffs


def send_bill_update_notifications(
    snapshots_by_bill_id,
):
    bill_diffs = _calculate_bill_diffs(snapshots_by_bill_id)

    if bill_diffs:
        logging.info("Bills were changed in this cron run, sending emails")
        _send_bill_update_emails(bill_diffs)
