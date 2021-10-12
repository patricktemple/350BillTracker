import logging

from flask import render_template
from sqlalchemy.orm import selectinload
from werkzeug import exceptions

from .models import Bill, Legislator, User
from .ses import send_email


class BillDiff:
    bill = None
    old_status = None
    added_sponsors = None  # lists the sponsor names
    removed_sponsors = None  # lists the sponsor names only

    def __repr__(self):
        return self.__dict__.__repr__()


class BillSnapshot:
    bill_id = None
    status = None
    sponsor_ids = []

    def __init__(self, bill_id, status, sponsor_ids):
        self.bill_id = bill_id  # needed?
        self.status = status
        self.sponsor_ids = sponsor_ids


def snapshot_bills():
    """Snapshots the state of all bills. Used to calculate the diff produced by
    a cron job run, so that we can send out email notifications of bill status changes."""
    bills = Bill.query.options(selectinload(Bill.sponsorships)).all()

    snapshots_by_bill_id = {}
    for bill in bills:
        sponsor_ids = [s.legislator_id for s in bill.sponsorships]
        snapshot = BillSnapshot(bill.id, bill.status, sponsor_ids)
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

    # Update to python 3.10 and use structural pattern matching?

    file = diff.bill.file
    if not diff.added_sponsors and not diff.removed_sponsors:
        return f"{file}'s status changed to {diff.bill.status}"

    if diff.old_status == diff.bill.status:
        if not diff.added_sponsors:
            return f"{file} lost {_get_sponsor_subject_string(diff.removed_sponsors)}"
        if not diff.removed_sponsors:
            return f"{file} gained {_get_sponsor_subject_string(diff.added_sponsors)}"
        return f"{file} gained and lost sponsors"

    return f"{diff.bill.file} was updated"


def send_bill_update_emails(bill_diffs):
    diffs_for_template = []
    # TODO figure out if we really need this middle layer BillDiff before converting it to the renderable thing
    for diff in bill_diffs:
        if diff.bill.status == diff.old_status:
            status_text = f"Status: {diff.bill.status} (unchanged)"
            status_color = "black"  # or bold?
        else:
            status_text = f"Status: {diff.old_status} --> {diff.bill.status}"
            status_color = "blue"

        if not diff.added_sponsors and not diff.removed_sponsors:
            sponsor_text = (
                f"{len(diff.bill.sponsorships)} sponsors (unchanged)"
            )
            sponsor_color = "black"
        else:
            new_sponsor_count = len(diff.bill.sponsorships)
            old_sponsor_count = (
                new_sponsor_count
                - len(diff.added_sponsors)
                + len(diff.removed_sponsors)
            )
            sponsor_color = "blue"

            explanations = []
            if diff.added_sponsors:
                explanations.append(f"gained {', '.join(diff.added_sponsors)}")
            if diff.removed_sponsors:
                explanations.append(f"lost {', '.join(diff.removed_sponsors)}")

            sponsor_text = f"{old_sponsor_count} sponsors --> {new_sponsor_count} sponsors ({', '.join(explanations)})"

        diffs_for_template.append(
            {
                "file": diff.bill.file,
                "display_name": diff.bill.display_name,
                "status_text": status_text,
                "status_color": status_color,
                "sponsor_text": sponsor_text,
                "sponsor_color": sponsor_color,
            }
        )

    subject = _get_bill_update_subject_line(bill_diffs)
    body_text = render_template(
        "bill_alerts_email.txt", diffs=diffs_for_template
    )
    body_html = render_template(
        "bill_alerts_email.html", diffs=diffs_for_template
    )

    users_to_notify = User.query.filter_by(
        send_bill_update_notifications=True
    ).all()

    for user in users_to_notify:
        logging.info(f"Sending bill update email to {user.email}")
        send_email(user.email, subject, body_html, body_text)


def send_bill_update_notifications(
    snapshots_by_bill_id,
):  # this modifies the snapshots
    bills = Bill.query.options(selectinload("sponsorships.legislator")).all()

    changed_bill_diffs = []
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
            diff.added_sponsors = [s.name for s in added_sponsors]
            diff.removed_sponsors = [s.name for s in removed_sponsors]
            changed_bill_diffs.append(diff)
            # It's possible that all this logic doesn't belong in the SES stuff

    if changed_bill_diffs:
        logging.info("Bills were changed in this cron run, sending emails")
        send_bill_update_emails(changed_bill_diffs)
