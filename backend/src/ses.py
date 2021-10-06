"""Utilities for using AWS's Simple Email Service to send emails."""

import logging

from boto3 import client
from botocore.exceptions import ClientError
from werkzeug import exceptions
from flask import render_template

# This guide was important in getting the email address set up:
# https://medium.com/responsetap-engineering/easily-create-email-addresses-for-your-route53-custom-domain-589d099dd0f2
client = client("ses")

SENDER = "350 Bill Tracker <no-reply@350billtracker.com>"
CHARSET = "UTF-8"


def send_login_link_email(email_address, login_link):
    BODY_TEXT = render_template("email.txt", login_link=login_link)
    BODY_HTML = render_template("email.html", login_link=login_link)

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
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
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
