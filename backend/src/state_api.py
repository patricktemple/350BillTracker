import logging
from dataclasses import dataclass

import requests

from .bill.models import (AssemblyBill, Bill, SenateBill, StateBill,
                          StateChamber)
from .models import db
from .person.models import AssemblyMember, Person, Senator
from .settings import SENATE_API_TOKEN
from .sponsorship.models import AssemblySponsorship, SenateSponsorship

# API docs: https://legislation.nysenate.gov/static/docs/html/
# See also https://www.nysenate.gov/how-bill-becomes-law

# Test bills for development
# CCIA: https://nyassembly.gov/leg/?term=2021&bn=S04264
CCIA_ASSEMBLY_ID = "A06967"
CCIA_SENATE_ID = "S04264"
CCIA_TERM = "2021"



def senate_get(path: str, **params):
    response = requests.get(
        f"https://legislation.nysenate.gov/api/3/{path}",
        params={**params, "key": SENATE_API_TOKEN},
    )
    response.raise_for_status()
    return response.json()["result"]



# senate_bill = load_bill(CCIA_SENATE_ID)
# assembly_bill = load_bill(CCIA_ASSEMBLY_ID)

# TO get a bill:

def print_status(print_no):
    senate_response = senate_get(f"bills/{CCIA_TERM}/{print_no}", view="no_fulltext")
    amendments = list(senate_response['amendments']['items'].values())
    same_as = []
    for a in amendments:
        if 'sameAs' in a:
            items = a['sameAs']['items']
            if items:
                # NOTE: This does not
                base_print_no = items[0]['basePrintNo']
                assembly_response = senate_get(f"bills/2021/{base_print_no}", view="no_fulltext")
                print(f"{print_no}\t{senate_response['status']['statusDesc']}\t{senate_response['billType']['resolution']}\t{base_print_no}\t{assembly_response['status']['statusDesc']}\t{assembly_response['billType']['resolution']}")
                return
    
    # if same_as:
    #     first = same_as[0]
    #     for i in range(1, len(same_as)):
    #         if same_as[i] != first:
    #             print(f"Not equal! {print_no}")
    #             break

def do():
    for i in range(4000, 4270):
        print_status(f"S{i}")
    
def import_bill(session_year, senate_print_no):
    response = senate_get(f"bills/{session_year}/{senate_print_no}", view="no_fulltext")

    # Right now this will just keep inserting duplicates
    bill = Bill(type=Bill.BillType.STATE, name=response['title'], description=response['summary'])
    bill.state_bill = StateBill(
        session_year=session_year)
    bill.state_bill.senate_bill = SenateBill(
        status=response['status']['statusDesc'],
        base_print_no=response['basePrintNo'],
        active_version_name=response['activeVersion'])     # TODO rename to active_version

    active_amendment = response["amendments"]["items"][
         bill.state_bill.senate_bill.active_version_name
    ]

    for sponsor in active_amendment['coSponsors']['items']:
        # TODO also include lead sponsor, it's its own field on main bill
        member_id = sponsor['memberId']
        senator = Senator.query.filter_by(state_member_id=member_id).one_or_none()
        if senator:
            sponsorship = SenateSponsorship(senator_id=senator.person_id)
            bill.state_bill.senate_bill.sponsorships.append(sponsorship)
            logging.info(f"Added sponsorship for {senator.person.name} to bill {senate_print_no}")
        else:
            logging.warning(f"Did not find {sponsor['fullName']}, member_id: {member_id} for sponsorship on bill {senate_print_no}")

    same_as_versions = active_amendment['sameAs']['items']
    if same_as_versions:
        assembly_print_no = same_as_versions[0]['basePrintNo']
        assembly_response = senate_get(f"bills/{session_year}/{assembly_print_no}", view="no_fulltext")
        bill.state_bill.assembly_bill = AssemblyBill(
            status=assembly_response['status']['statusDesc'],
            base_print_no=assembly_response['basePrintNo'],
            active_version_name=assembly_response['activeVersion']
        )
    
    # TODO: assembly sponsorships

    db.session.add(bill)
    db.session.commit()
    return bill
    
def lookup_people(session_year):
    members = senate_get(f"members/{session_year}?limit=1000&full=true")
    for member in members['items']:
        person = Person(name=member['person']['fullName'], title=member['person']['prefix'], email=member['person']['email'])
        if member['chamber'] == 'ASSEMBLY':
            person.type = Person.PersonType.ASSEMBLY_MEMBER
            person.assembly_member = AssemblyMember(state_person_id=member['person']['personId'], state_member_id=member['memberId'])
            # We may need to track their Member ID too? Depends on what the bill sponsorship uses to identify people
        elif member['chamber'] == 'SENATE':
            person.type = Person.PersonType.SENATOR
            person.senator = Senator(state_person_id=member['person']['personId'], state_member_id=member['memberId'])
        else:
            # ???
            pass

        db.session.add(person)
    
    db.session.commit()


def _convert_search_results(state_bill):
    input = state_bill['result']
    result = {
        "type": Bill.BillType.STATE,
        "name": input['title'],
        "description": input['summary'],
        "session_year": input['session'],
        'base_print_no': input['basePrintNo'],
        'active_version': input['activeVersion'],
        'status': input['status']['statusDesc'],
        "chamber": StateChamber.SENATE if input['billType']['chamber'] == 'SENATE' else StateChamber.ASSEMBLY,
    }
    # active_amendment = input['amendments'][input['activeVersion']]
    # if active_amendment['']
    return result


def search_bills(code_name, session_year=None):
    terms = [
        f"(basePrintNo:{code_name} OR printNo:{code_name})",
        "billType.resolution:false"
    ]
    if session_year:
        terms.append(f"session:{session_year}")
    
    response = senate_get(f"bills/search", term=" AND ".join(terms))
    return [_convert_search_results(item) for item in response['items']]