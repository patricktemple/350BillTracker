import logging

import requests

from .bill.models import (
    AssemblyBill,
    Bill,
    SenateBill,
    StateBill,
    StateChamber,
)
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

CURRENT_SESSION_YEAR = "2021"


def senate_get(path: str, **params):
    response = requests.get(
        f"https://legislation.nysenate.gov/api/3/{path}",
        params={**params, "key": SENATE_API_TOKEN},
    )
    response.raise_for_status()
    return response.json()["result"]


# todo put types on the args
def _add_senate_sponsorships(bill, chamber_data):
    active_amendment = chamber_data["amendments"]["items"][
        chamber_data["activeVersion"]
    ]
    for sponsor in active_amendment["coSponsors"]["items"]:
        # TODO also include lead sponsor, it's its own field on main bill
        member_id = sponsor["memberId"]
        senator = Senator.query.filter_by(
            state_member_id=member_id
        ).one_or_none()
        if senator:
            sponsorship = SenateSponsorship(senator_id=senator.person_id)
            bill.state_bill.senate_bill.sponsorships.append(sponsorship)
            logging.info(
                f"Added sponsorship for {senator.person.name} to bill {bill.state_bill.senate_bill.base_print_no}"
            )
        else:
            logging.warning(
                f"Did not find {sponsor['fullName']}, member_id: {member_id} for sponsorship on bill {bill.state_bill.senate_bill.base_print_no}"
            )


# dedupe with above?
def _add_assembly_sponsorships(bill, chamber_data):
    active_amendment = chamber_data["amendments"]["items"][
        chamber_data["activeVersion"]
    ]
    for sponsor in active_amendment["coSponsors"]["items"]:
        # TODO also include lead sponsor, it's its own field on main bill
        member_id = sponsor["memberId"]
        assembly_member = AssemblyMember.query.filter_by(
            state_member_id=member_id
        ).one_or_none()
        if assembly_member:
            sponsorship = AssemblySponsorship(
                assembly_member_id=assembly_member.person_id
            )
            bill.state_bill.assembly_bill.sponsorships.append(sponsorship)
            logging.info(
                f"Added sponsorship for {assembly_member.person.name} to bill {bill.state_bill.assembly_bill.base_print_no}"
            )
        else:
            logging.warning(
                f"Did not find {sponsor['fullName']}, member_id: {member_id} for sponsorship on bill {bill.state_bill.assembly_bill.base_print_no}"
            )


def _update_bill_sponsorships(bill):
    pass


def update_all_sponsorships():
    bills = StateBill.query.all()
    for bill in bills:
        _update_bill_sponsorships(bill)
        # error handling


def import_bill(session_year, base_print_no):
    """TODO comment

    this can insert duplicates but application logic should prevent that
    """
    initial_chamber_response = senate_get(
        f"bills/{session_year}/{base_print_no}", view="no_fulltext"
    )

    # todo filter out resolutions

    bill = Bill(
        type=Bill.BillType.STATE,
        name=initial_chamber_response["title"],
        description=initial_chamber_response["summary"],
    )
    bill.state_bill = StateBill(session_year=session_year)

    active_amendment = initial_chamber_response["amendments"]["items"][
        initial_chamber_response["activeVersion"]
    ]

    initial_chamber = initial_chamber_response["billType"]["chamber"]

    same_as_versions = active_amendment["sameAs"]["items"]
    alternate_chamber_response = None
    if same_as_versions:
        same_as_print_no = same_as_versions[0]["basePrintNo"]
        alternate_chamber_response = senate_get(
            f"bills/{session_year}/{same_as_print_no}", view="no_fulltext"
        )

        if {
            initial_chamber,
            alternate_chamber_response["billType"]["chamber"],
        } != {"SENATE", "ASSEMBLY"}:
            alternate_chamber_response = None
            logging.error(
                f"Bill {session_year}/{base_print_no} had same_as={same_as_print_no}, in same chamber!"
            )

    if initial_chamber == "SENATE":
        senate_data = initial_chamber_response
        assembly_data = alternate_chamber_response
    else:
        senate_data = alternate_chamber_response
        assembly_data = initial_chamber_response

    if assembly_data:
        bill.state_bill.assembly_bill = AssemblyBill(
            status=assembly_data["status"]["statusDesc"],
            base_print_no=assembly_data["basePrintNo"],
            active_version=assembly_data["activeVersion"],
        )
        _add_assembly_sponsorships(bill, assembly_data)
    if senate_data:
        bill.state_bill.senate_bill = SenateBill(
            status=senate_data["status"]["statusDesc"],
            base_print_no=senate_data["basePrintNo"],
            active_version=senate_data["activeVersion"],
        )
        _add_senate_sponsorships(bill, senate_data)

    db.session.add(bill)
    db.session.commit()
    return bill


def add_state_representatives(session_year=CURRENT_SESSION_YEAR):
    """TODO comment"""
    members = senate_get(f"members/{session_year}?limit=1000&full=true")
    for member in members["items"]:
        member_id = member["memberId"]
        if member["chamber"] == "ASSEMBLY":
            person_type = Person.PersonType.ASSEMBLY_MEMBER
            existing_member = AssemblyMember.query.filter_by(
                state_member_id=member_id
            ).one_or_none()
        elif member["chamber"] == "SENATE":
            person_type = Person.PersonType.SENATOR
            existing_member = Senator.query.filter_by(
                state_member_id=member_id
            ).one_or_none()
        else:
            # ???
            pass

        if existing_member:
            logging.info(
                f"Person {existing_member.person.name} already in DB, updating"
            )
            person = existing_member.person
        else:
            logging.info(f"Adding person {member['person']['fullName']}")
            person = Person(type=person_type)
            if person_type == Person.PersonType.ASSEMBLY_MEMBER:
                person.assembly_member = AssemblyMember(
                    state_member_id=member_id
                )
            else:
                person.senator = Senator(state_member_id=member_id)
            db.session.add(person)

        person.name = member["person"]["fullName"]
        person.title = member["person"]["prefix"]
        person.email = member["person"]["email"]

    db.session.commit()


def fill_state_representative_static_data():
    # TODO: Implement
    pass


def _convert_search_results(state_bill):
    input = state_bill["result"]
    result = {
        "type": Bill.BillType.STATE,
        "name": input["title"],
        "description": input["summary"],
        "session_year": input["session"],
        "base_print_no": input["basePrintNo"],
        "active_version": input["activeVersion"],
        "status": input["status"]["statusDesc"],
        "chamber": StateChamber.SENATE
        if input["billType"]["chamber"] == "SENATE"
        else StateChamber.ASSEMBLY,
    }
    # active_amendment = input['amendments'][input['activeVersion']]
    # if active_amendment['']
    return result


def search_bills(code_name, session_year=None):
    terms = [
        f"(basePrintNo:{code_name} OR printNo:{code_name})",
        "billType.resolution:false",
    ]
    if session_year:
        terms.append(f"session:{session_year}")

    response = senate_get("bills/search", term=" AND ".join(terms))
    return [_convert_search_results(item) for item in response["items"]]
