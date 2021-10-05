"""Utilities for using AWS's Simple Email Service to send emails."""

import boto3
from botocore.exceptions import ClientError

from .settings import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_SECRET_ACCESS_KEY,
)

# This guide was important in getting the email address set up:
# https://medium.com/responsetap-engineering/easily-create-email-addresses-for-your-route53-custom-domain-589d099dd0f2
client = boto3.client("ses")

# TODO: Need to enable this app for non-SES sandbox so it can send to unverified email.

SENDER = "350 Bill Tracker <no-reply@350billtracker.com>"
CHARSET = "UTF-8"


def send_login_link_email(email_address, login_link):
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (
        "350 Bill Tracker.\r\n"
        f"Go to the following link to log in:\r\n{login_link}"
    )

    # TODO: Use better template
    # The HTML body of the email.
    BODY_HTML = (
        """<html>
  <head></head>
  <body>
    <h1>Log in to 350 Bill tracker</h1>"""
        f'<p>Click <a href="{login_link}">here</a> to log in.</p>'
        """</body>
      </html>"""
    )

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
    # TODO: Better error handling
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])