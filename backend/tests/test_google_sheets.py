from unittest.mock import Mock, MagicMock, patch

from src import app
from src.utils import now
from src.models import Bill, db
from src.google_sheets import create_phone_bank_spreadsheet

# TODO: Need to set test environment variables so we don't accidentally call real APIs
@patch("src.google_sheets.Credentials")
def test_generate_google_sheet(mock_credentials):
  bill = Bill(id=1234, file="Intro 3", name="Ban oil", title="Ban all oil", intro_date=now())
  db.session.add(bill)
  db.session.commit()

  create_phone_bank_spreadsheet(1234)
  raise ValueError("not implemented")