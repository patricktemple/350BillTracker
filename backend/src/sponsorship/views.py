from typing import Union
from uuid import UUID

from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required
from ..bill.models import CityBill, StateBill
from ..person.models import AssemblyMember, Person, Senator
from .models import AssemblySponsorship, CitySponsorship, SenateSponsorship
from .schema import (
    CouncilMemberSponsorshipSchema,
    SponsorListSchema,
    StateBillSponsorshipsSchema,
    StateRepresenativeSponsorshipSchema,
)


@app.route(
    "/api/council-members/<uuid:council_member_id>/sponsorships",
    methods=["GET"],
)
@auth_required
def council_member_sponsorships(council_member_id):
    sponsorships = (
        CitySponsorship.query.filter_by(council_member_id=council_member_id)
        .options(joinedload(CitySponsorship.bill))
        .all()
    )
    return CouncilMemberSponsorshipSchema(many=True).jsonify(sponsorships)


@app.route("/api/city-bills/<uuid:bill_id>/sponsorships", methods=["GET"])
@auth_required
def city_bill_sponsorships(bill_id):
    city_bill = CityBill.query.get(bill_id)
    if not city_bill:
        raise exceptions.NotFound()
    sponsorships = (
        CitySponsorship.query.filter_by(bill_id=bill_id)
        .options(joinedload(CitySponsorship.person))
        .order_by(CitySponsorship.sponsor_sequence)
        .all()
    )
    non_sponsors = (
        Person.query.filter(
            Person.id.not_in([s.council_member_id for s in sponsorships])
            & (Person.type == Person.PersonType.COUNCIL_MEMBER)
        )
        .order_by(Person.name)
        .all()
    )
    if sponsorships and sponsorships[0].sponsor_sequence == 0:
        lead_sponsor = sponsorships[0].person
        sponsorships.pop(0)
    else:
        lead_sponsor = None
    return SponsorListSchema().jsonify(
        {
            "lead_sponsor": lead_sponsor,
            "cosponsors": [s.person for s in sponsorships],
            "non_sponsors": non_sponsors,
        }
    )


def _get_state_sponsorship_list(
    sponsorship_model: Union[SenateSponsorship, AssemblySponsorship],
    representative_model: Union[Senator, AssemblyMember],
    bill_id: UUID,
):
    sponsorships = (
        sponsorship_model.query.filter_by(bill_id=bill_id)
        .options(joinedload(sponsorship_model.representative))
        .all()
    )
    cosponsors = (
        s.representative.person for s in sponsorships if not s.is_lead_sponsor
    )
    lead_sponsor_list = [
        s.representative.person for s in sponsorships if s.is_lead_sponsor
    ]
    lead_sponsor = lead_sponsor_list[0] if lead_sponsor_list else None
    non_sponsors = representative_model.query.filter(
        representative_model.person_id.not_in(
            [s.person_id for s in sponsorships]
        )
    ).all()

    return lead_sponsor, cosponsors, (r.person for r in non_sponsors)


@app.route("/api/state-bills/<uuid:bill_id>/sponsorships", methods=["GET"])
@auth_required
def state_bill_sponsorships(bill_id):
    state_bill = StateBill.query.get(bill_id)
    if not state_bill:
        raise exceptions.NotFound()

    (
        senate_lead_sponsor,
        senate_cosponsors,
        senate_non_sponsors,
    ) = _get_state_sponsorship_list(SenateSponsorship, Senator, bill_id)

    (
        assembly_lead_sponsor,
        assembly_cosponsors,
        assembly_non_sponsors,
    ) = _get_state_sponsorship_list(
        AssemblySponsorship, AssemblyMember, bill_id
    )

    return StateBillSponsorshipsSchema().jsonify(
        {
            "bill_id": bill_id,
            "senate_sponsorships": {
                "lead_sponsor": senate_lead_sponsor,
                "cosponsors": senate_cosponsors,
                "non_sponsors": senate_non_sponsors,
            },
            "assembly_sponsorships": {
                "lead_sponsor": assembly_lead_sponsor,
                "cosponsors": assembly_cosponsors,
                "non_sponsors": assembly_non_sponsors,
            },
        }
    )


@app.route("/api/senators/<uuid:person_id>/sponsorships", methods=["GET"])
@auth_required
def senator_sponsorships(person_id):
    sponsorships = (
        SenateSponsorship.query.filter_by(person_id=person_id)
        .options(joinedload(SenateSponsorship.bill))
        .all()
    )

    return StateRepresenativeSponsorshipSchema(many=True).jsonify(sponsorships)


@app.route(
    "/api/assembly-members/<uuid:person_id>/sponsorships", methods=["GET"]
)
@auth_required
def assembly_member_sponsorships(person_id):
    sponsorships = (
        AssemblySponsorship.query.filter_by(person_id=person_id)
        .options(joinedload(AssemblySponsorship.bill))
        .all()
    )

    return StateRepresenativeSponsorshipSchema(many=True).jsonify(sponsorships)
