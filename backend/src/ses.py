"""Utilities for using AWS's Simple Email Service to send emails."""

import logging
from operator import add

from boto3 import client
from botocore.exceptions import ClientError
from flask import render_template
from werkzeug import exceptions

from .settings import APP_TITLE
from .models import Bill, Legislator
from sqlalchemy.orm import selectinload

# This guide was important in getting the email address set up:
# https://medium.com/responsetap-engineering/easily-create-email-addresses-for-your-route53-custom-domain-589d099dd0f2
client = client("ses")

SENDER = f"{APP_TITLE} <no-reply@350billtracker.com>"
CHARSET = "UTF-8"


class BillDiff:
    bill = None
    old_status = None
    added_sponsors = None
    removed_sponsors = None


    def __repr__(self):
        return self.__dict__.__repr__()


def send_bill_update_notifications(snapshots_by_bill_id): # this modifies the snapshots
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
            removed_sponsors = Legislator.query.filter(Legislator.id.in_(prior_sponsor_ids)).all()
        else:
            removed_sponsors = []
        
        if removed_sponsors or added_sponsors or bill.status != snapshot.status:
            diff = BillDiff()
            diff.bill = bill
            diff.old_status = snapshot.status
            diff.added_sponsors = added_sponsors
            diff.removed_sponsors = removed_sponsors
            changed_bill_diffs.append(diff)
    
    if changed_bill_diffs:
        # Send an email
        # TODO be more specific when possible, and do plural
        subject = f"{len(changed_bill_diffs)} bills updated"
        email_address = "patricktemple@gmail.com" # TODO change this!
    
        # Make this another function!
        body_text = changed_bill_diffs.__repr__()

        try:
            response = client.send_email(
                Destination={
                    "ToAddresses": [
                        email_address
                    ],
                },
                Message={
                    "Body": {
                        # "Html": {
                        #     "Charset": CHARSET,
                        #     "Data": body_html,
                        # },
                        "Text": {
                            "Charset": CHARSET,
                            "Data": body_text,
                        },
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": subject,
                    },
                },
                Source=SENDER,
            )
        except ClientError as e:
            logging.exception(e)
            raise exceptions.ServiceUnavailable("Could not send email")
        else:
            logging.info(
                f"Email sent successfully to {email_address}, message ID: {response['MessageId']}"
            )


def send_login_link_email(email_address, login_link):
    body_text = render_template("login_email.txt", login_link=login_link)
    body_html = render_template("login_email.html", login_link=login_link)

    try:
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    email_address,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": body_html,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": body_text,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": "Log in to 350 Bill Tracker",
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        logging.exception(e)
        raise exceptions.ServiceUnavailable("Could not send email")
    else:
        logging.info(
            f"Email sent successfully to {email_address}, message ID: {response['MessageId']}"
        )
