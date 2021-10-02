import os
from base64 import b64decode

CITY_COUNCIL_API_TOKEN = os.environ.get("CITY_COUNCIL_API_TOKEN")

GOOGLE_CREDENTIALS = b64decode(
    os.environ["GOOGLE_CREDENTIALS"].encode("utf-8")
).decode("utf-8")

JWT_SECRET = "TODO make a real secret"


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
