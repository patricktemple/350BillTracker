from .settings import SENATE_API_TOKEN
from dataclasses import dataclass

import requests

# API docs: https://legislation.nysenate.gov/static/docs/html/
# See also https://www.nysenate.gov/how-bill-becomes-law

# Test bills for development
# CCIA: https://nyassembly.gov/leg/?term=2021&bn=S04264
CCIA_ASSEMBLY_ID = "A06967"
CCIA_SENATE_ID = "S04264"
CCIA_TERM = "2021"

def senate_get(path: str, **params):
    response = requests.get(f"https://legislation.nysenate.gov/api/3/{path}", params={
        **params,
        'key': SENATE_API_TOKEN
    })
    response.raise_for_status()
    return response.json()['result']

# This includes every amendment version.
# assembly_bill = senate_get(f"bills/{CCIA_TERM}/{CCIA_ASSEMBLY_ID}", view="no_fulltext")

@dataclass
class SenateBill:
    session: int = None
    print_no: str = None
    active_amendment_version: str = None
    lead_sponsor: str = None# just the name, for now
    cosponsors: str = None

    title: str = None
    summary: str = None
    status: str = None

    # TODO: Add links to senate and assembly pages too
    # In scope: just track things for the power hour and email notifications
    # Out of scope: recreate all bill tracking, including hearings, votes etc

def load_bill(print_no):
    response = senate_get(f"bills/{CCIA_TERM}/{print_no}", view="no_fulltext")
    bill = SenateBill()
    bill.active_amendment_version = response['activeVersion']
    bill.lead_sponsor = response['sponsor']['member']['fullName']

    active_amendment = response['amendments']['items'][bill.active_amendment_version]
    bill.cosponsors = [cs['fullName'] for cs in active_amendment['coSponsors']['items']]

    bill.title = response['title']
    bill.summary = response['summary']
    bill.status = response['status']['statusDesc']
    bill.print_no = response['basePrintNo'] # excludes amendment suffix. could do printNo to include it
    bill.session = response['session']
    return bill

senate_bill = load_bill(CCIA_SENATE_ID)
assembly_bill = load_bill(CCIA_ASSEMBLY_ID)

# TO get a bill:
# 1) Get the full payload result
# 2) Get the active amendment version. Track that as a field, but for the sake of our tracking, we only care about latest amendment
# 3) Look at that amendment, pull out the co-sponsor list.
# 4) Question: if bill is amended, what happens to the existing sponsor list?