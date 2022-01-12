"""Utilities for using AWS's Simple Email Service to send emails."""

import logging

from boto3 import client
from botocore.exceptions import ClientError
from flask import render_template
from werkzeug import exceptions

from .settings import APP_TITLE

# This guide was important in getting the email address set up:
# https://medium.com/responsetap-engineering/easily-create-email-addresses-for-your-route53-custom-domain-589d099dd0f2
client = client("ses")

SENDER = f"{APP_TITLE} <no-reply@350billtracker.com>"
CHARSET = "UTF-8"


def send_email(email, subject, body_html, body_text):
    response = client.send_email(
        Destination={
            "ToAddresses": [email],
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
                "Data": subject,
            },
        },
        Source=SENDER,
    )
    logging.info(
        f"Email sent successfully to {email}, message ID: {response['MessageId']}"
    )


def send_login_link_email(email_address, login_link):
    body_text = render_template("login_email.txt", login_link=login_link)
    body_html = render_template("login_email.html", login_link=login_link)

    try:
        send_email(
            email_address, "Log in to 350 Bill Tracker", body_html, body_text
        )
    except ClientError as e:
        logging.exception(e)
        raise exceptions.ServiceUnavailable("Could not send email")
