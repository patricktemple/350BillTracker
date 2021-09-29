"""Generates credentials to access a specific user's calendar in order
to sync events to it. Will open a browser-based OAuth consent form when run.
"""

from __future__ import print_function

from base64 import b64encode
from datetime import datetime, timezone

from google_auth_oauthlib.flow import InstalledAppFlow

from src import app
from src.google_sheets import SCOPES


def print_google_creds():
    # This secret was taken when I configured the Google Cloud app for TogglSync.
    flow = InstalledAppFlow.from_client_secrets_file(
        ".secret/credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)
    creds_json = creds.to_json()
    print(f"JSON token:\n{creds_json}\n")

    creds_b64 = b64encode(creds_json.encode("utf-8")).decode("utf-8")
    print(
        f"Base64-encoded token (set GOOGLE_CREDENTIALS to this):\n{creds_b64}"
    )


def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


if __name__ == "__main__":
    print_google_creds()
