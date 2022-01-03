from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required
from ..bill.models import CityBill, StateBill
from ..person.models import AssemblyMember, Person, Senator
from .models import AssemblySponsorship, CitySponsorship, SenateSponsorship
from .schema import (CityBillSponsorshipSchema, CouncilMemberSponsorshipSchema,
                     StateBillSponsorshipsSchema)


# TODO: Figure out routes for people
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
    for sponsorship in sponsorships:
        # This is not a field on the SQLA object, but we set it so that it gets
        # serialized into the response.
        sponsorship.is_sponsor = True

    non_sponsors = (
        Person.query.filter(
            Person.id.not_in([s.council_member_id for s in sponsorships])
            & (Person.type == Person.PersonType.COUNCIL_MEMBER)
        )
        .order_by(Person.name)
        .all()
    )
    non_sponsorships = [
        {
            "bill_id": bill_id,
            "is_sponsor": False,
            "person": person,
        }
        for person in non_sponsors
    ]
    return CityBillSponsorshipSchema(many=True).jsonify(
        sponsorships + non_sponsorships
    )


@app.route("/api/state-bills/<uuid:bill_id>/sponsorships", methods=["GET"])
@auth_required
def state_bill_sponsorships(bill_id):
    state_bill = StateBill.query.get(bill_id)
    if not state_bill:
        raise exceptions.NotFound()
    
    senate_sponsorships = (
        SenateSponsorship.query.filter_by(senate_version_id=state_bill.senate_bill.id)
        .options(joinedload(SenateSponsorship.senator))
        .all()
    )
    senate_non_sponsors = Senator.query.filter(Senator.person_id.not_in([s.senator_id for s in senate_sponsorships])).all()

    assembly_sponsorships = (
        AssemblySponsorship.query.filter_by(assembly_version_id=state_bill.assembly_bill.id)
        .options(joinedload(AssemblySponsorship.assembly_member))
        .all()
    )
    assembly_non_sponsors = AssemblyMember.query.filter(AssemblyMember.person_id.not_in([s.assembly_member_id for s in assembly_sponsorships])).all()

    return StateBillSponsorshipsSchema().jsonify({
        "bill_id": bill_id,
        "senate_sponsors": (s.senator.person for s in senate_sponsorships),
        "senate_non_sponsors": (s.person for s in senate_non_sponsors),
        "assembly_sponsors": (s.assembly_member.person for s in assembly_sponsorships),
        "assembly_non_sponsors": (a.person for a in assembly_non_sponsors),
    })
