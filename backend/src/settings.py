import os
from base64 import b64decode

CITY_COUNCIL_API_TOKEN = os.environ.get("CITY_COUNCIL_API_TOKEN")

GOOGLE_CREDENTIALS = b64decode(
    os.environ["GOOGLE_CREDENTIALS"].encode("utf-8")
).decode("utf-8")

JWT_SECRET = os.environ["JWT_SECRET"]

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_DEFAULT_REGION = os.environ["AWS_DEFAULT_REGION"]

APP_ORIGIN = os.environ["APP_ORIGIN"]

ENABLE_CRON = os.environ.get("ENABLE_CRON", "True") == "True"

APP_TITLE = os.environ.get("APP_TITLE", "350 Brooklyn Bill Tracker")

SENATE_API_TOKEN = os.environ["SENATE_API_TOKEN"]


# TODO: Share this with TogglSync via a utils package?
if hostname := os.environ.get("RDS_HOSTNAME"):
    # When running on Beanstalk, it automatically sets all these values for the attached RDS:
    username = os.environ["RDS_USERNAME"]
    password = os.environ["RDS_PASSWORD"]
    db_name = os.environ["RDS_DB_NAME"]
    port = os.environ["RDS_PORT"]
    DATABASE_URL = (
        f"postgresql://{username}:{password}@{hostname}:{port}/{db_name}"
    )
else:
    # For local development
    DATABASE_URL = os.environ["DATABASE_URL"]
