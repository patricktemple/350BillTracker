import logging
from typing import Optional, Union

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
from .utils import cron_function

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


def _add_sponsorship(
    *,
    chamber_bill,
    sponsor_data,
    sponsorship_model: Union[AssemblySponsorship, SenateSponsorship],
    representative_model: Union[AssemblyMember, Senator],
    is_lead_sponsor,
):
    member_id = sponsor_data["memberId"]
    representative = representative_model.query.filter_by(
        state_member_id=member_id
    ).one_or_none()
    if representative:
        sponsorship = sponsorship_model(
            person_id=representative.person_id,
            is_lead_sponsor=is_lead_sponsor,
        )
        chamber_bill.sponsorships.append(sponsorship)
        logging.info(
            f"Added sponsorship for {representative.person.name} to bill {chamber_bill.base_print_no}"
        )
    else:
        logging.warning(
            f"Did not find {sponsor_data['fullName']}, member_id: {member_id} for sponsorship on bill {chamber_bill.base_print_no}"
        )


def _add_chamber_sponsorships(
    *,
    chamber_bill,
    chamber_data,
    sponsorship_model: Union[AssemblySponsorship, SenateSponsorship],
    representative_model: Union[AssemblyMember, Senator],
):
    active_amendment = chamber_data["amendments"]["items"][
        chamber_data["activeVersion"]
    ]
    lead_sponsor = chamber_data["sponsor"]["member"]
    _add_sponsorship(
        chamber_bill=chamber_bill,
        sponsor_data=lead_sponsor,
        sponsorship_model=sponsorship_model,
        representative_model=representative_model,
        is_lead_sponsor=True,
    )
    for sponsor in active_amendment["coSponsors"]["items"]:
        _add_sponsorship(
            chamber_bill=chamber_bill,
            sponsor_data=sponsor,
            sponsorship_model=sponsorship_model,
            representative_model=representative_model,
            is_lead_sponsor=False,
        )


def _extract_alternate_chamber_print_no(chamber_response):
    active_amendment = chamber_response["amendments"]["items"][
        chamber_response["activeVersion"]
    ]
    same_as_versions = active_amendment["sameAs"]["items"]
    if not same_as_versions:
        return None

    return same_as_versions[0]["basePrintNo"]


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

    initial_chamber = initial_chamber_response["billType"]["chamber"]
    same_as_print_no = _extract_alternate_chamber_print_no(
        initial_chamber_response
    )
    alternate_chamber_response = None
    if same_as_print_no:
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
            chamber_bill=bill.state_bill.assembly_bill,
            chamber_data=assembly_data,
            sponsorship_model=AssemblySponsorship,
            representative_model=AssemblyMember,
        )
    if senate_data:
        bill.state_bill.senate_bill = SenateBill(
            status=senate_data["status"]["statusDesc"],
            base_print_no=senate_data["basePrintNo"],
            active_version=senate_data["activeVersion"],
        )
        _add_chamber_sponsorships(
            chamber_bill=bill.state_bill.senate_bill,
            chamber_data=senate_data,
            sponsorship_model=SenateSponsorship,
            representative_model=Senator,
        )

    db.session.add(bill)
    db.session.commit()
    return bill


@cron_function
def sync_state_representatives(session_year=CURRENT_SESSION_YEAR):
    """Queries the NY State API to retrieve all senators and assembly members
    in the current session year. If they already exist in the DB, updates
    their contact info."""

    members = senate_get(f"members/{session_year}?limit=1000&full=true")

    for member in members["items"]:
        if not member["incumbent"]:
            # TODO: Properly handle removal of old reps
            continue
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


def _update_state_chamber_bill(
    chamber_bill: Union[SenateBill, AssemblyBill],
    sponsorship_model: Union[SenateSponsorship, AssemblySponsorship],
    representative_model: Union[Senator, AssemblyMember],
    alternate_chamber_bill: Union[SenateBill, AssemblyBill],
):
    chamber_response = senate_get(
        f"bills/{chamber_bill.state_bill.session_year}/{chamber_bill.base_print_no}",
        view="no_fulltext",
    )

    alternate_print_no = (
        alternate_chamber_bill.base_print_no
        if alternate_chamber_bill
        else None
    )
    new_alternate_print_no = _extract_alternate_chamber_print_no(
        chamber_response
    )
    if alternate_print_no != new_alternate_print_no:
        # This is severe, but it's unclear what the right automatic fix is. It
        # would be good to get email alerts on it.
        logging.error(
            f"When updating bill {chamber_bill.base_print_no}, expected same_as to stay as {alternate_print_no} but it was {new_alternate_print_no}"
        )

    # Note that when there's a senate and assembly chamber both updating,
    # they'll both write these Bill fields, probably to the same values:
    bill = chamber_bill.state_bill.bill
    bill.name = chamber_response["title"]
    bill.description = chamber_response["summary"]

    chamber_bill.active_version = chamber_response["activeVersion"]
    chamber_bill.status = chamber_response["status"]["statusDesc"]

    chamber_bill.sponsorships.clear()
    _add_chamber_sponsorships(
        chamber_bill=chamber_bill,
        chamber_data=chamber_response,
        sponsorship_model=sponsorship_model,
        representative_model=representative_model,
    )



@cron_function
def update_state_bills():
    state_bills = StateBill.query.all()
    for state_bill in state_bills:
        try:
            if state_bill.senate_bill:
                _update_state_chamber_bill(
                    state_bill.senate_bill,
                    SenateSponsorship,
                    Senator,
                    state_bill.assembly_bill,
                )
            if state_bill.assembly_bill:
                _update_state_chamber_bill(
                    state_bill.assembly_bill,
                    AssemblySponsorship,
                    AssemblyMember,
                    state_bill.senate_bill,
                )

            db.session.commit()
        except Exception:
            db.session.rollback()
            logging.exception(f"Unhandled exception when updating bill {state_bill.bill.code_name}")


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
