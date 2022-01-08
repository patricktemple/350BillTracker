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


# TODO: Dedupe these fuctions!
def _add_senate_sponsorship(bill, sponsor_data, is_lead_sponsor):
    member_id = sponsor_data["memberId"]
    senator = Senator.query.filter_by(state_member_id=member_id).one_or_none()
    if senator:
        sponsorship = SenateSponsorship(
            senator_id=senator.person_id, is_lead_sponsor=is_lead_sponsor
        )
        bill.state_bill.senate_bill.sponsorships.append(sponsorship)
        logging.info(
            f"Added sponsorship for {senator.person.name} to bill {bill.state_bill.senate_bill.base_print_no}"
        )
    else:
        logging.warning(
            f"Did not find {sponsor_data['fullName']}, member_id: {member_id} for sponsorship on bill {bill.state_bill.senate_bill.base_print_no}"
        )


def _add_assembly_sponsorship(bill, sponsor_data, is_lead_sponsor):
    member_id = sponsor_data["memberId"]
    assembly_member = AssemblyMember.query.filter_by(
        state_member_id=member_id
    ).one_or_none()
    if assembly_member:
        # TODO: I can rename the field "assembly_member_id" and then this function can work for both chambers, it's simpler
        # and that can become a mixin.
        sponsorship = AssemblySponsorship(
            assembly_member_id=assembly_member.person_id,
            is_lead_sponsor=is_lead_sponsor,
        )
        bill.state_bill.assembly_bill.sponsorships.append(sponsorship)
        logging.info(
            f"Added sponsorship for {assembly_member.person.name} to bill {bill.state_bill.assembly_bill.base_print_no}"
        )
    else:
        logging.warning(
            f"Did not find {sponsor_data['fullName']}, member_id: {member_id} for sponsorship on bill {bill.state_bill.assembly_bill.base_print_no}"
        )


def _add_chamber_sponsorships(bill, chamber_data, add_sponsorship_function):
    active_amendment = chamber_data["amendments"]["items"][
        chamber_data["activeVersion"]
    ]
    lead_sponsor = chamber_data["sponsor"]["member"]
    add_sponsorship_function(bill, lead_sponsor, True)
    for sponsor in active_amendment["coSponsors"]["items"]:
        # TODO also include lead sponsor, it's its own field on main bill
        add_sponsorship_function(bill, sponsor, False)


def _update_bill_sponsorships(bill):
    pass


def update_all_sponsorships():
    bills = StateBill.query.all()
    for bill in bills:
        _update_bill_sponsorships(bill)


def import_bill(session_year, base_print_no):
    """Looks up a bill in the State API and starts tracking it. In the state
    API, a "bill" represents either a senate or assembly bill, with linkages
    between the two. In our models, both senate and assembly are captured under
    a single StateBill. Thus, this first looks up the requested senate or assembly
    bill, and then it tries to find out the equivalent bill in the other chamber
    and track that too.
    """
    initial_chamber_response = senate_get(
        f"bills/{session_year}/{base_print_no}", view="no_fulltext"
    )

    # TODO: Filter out resolutions?
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
        _add_chamber_sponsorships(
            bill, assembly_data, _add_assembly_sponsorship
        )
    if senate_data:
        bill.state_bill.senate_bill = SenateBill(
            status=senate_data["status"]["statusDesc"],
            base_print_no=senate_data["basePrintNo"],
            active_version=senate_data["activeVersion"],
        )
        _add_chamber_sponsorships(bill, senate_data, _add_senate_sponsorship)

    db.session.add(bill)
    db.session.commit()
    return bill


def add_state_representatives(session_year=CURRENT_SESSION_YEAR):
    """Queries the NY State API to retrieve all senators and assembly members
    in the current session year. If they already exist in the DB, updates
    their contact info."""

    try:
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
                existing_member.district = member["districtCode"]
                logging.info(
                    f"Person {existing_member.person.name} already in DB, updating"
                )
                person = existing_member.person
            else:
                logging.info(f"Adding person {member['person']['fullName']}")
                person = Person(type=person_type)
                if person_type == Person.PersonType.ASSEMBLY_MEMBER:
                    person.assembly_member = AssemblyMember(
                        state_member_id=member_id,
                        district=member["districtCode"],
                    )
                else:
                    person.senator = Senator(
                        state_member_id=member_id,
                        district=member["districtCode"],
                    )
                db.session.add(person)

            person.name = member["person"]["fullName"]
            person.title = member["person"]["prefix"]
            person.email = member["person"]["email"]

        db.session.commit()
    except Exception:
        logging.exception(
            "Unhandled exception when adding state representatives"
        )


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
    return result


def search_bills(code_name, session_year=None):
    """Searches for a bill by print number and session year. Returns all
    matching results.
    """
    terms = [
        f"(basePrintNo:{code_name} OR printNo:{code_name})",
        "billType.resolution:false",
    ]
    if session_year:
        terms.append(f"session:{session_year}")

    response = senate_get("bills/search", term=" AND ".join(terms))
    return [_convert_search_results(item) for item in response["items"]]
