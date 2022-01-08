from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required
from ..bill.models import CityBill, StateBill
from ..person.models import AssemblyMember, Person, Senator
from .models import AssemblySponsorship, CitySponsorship, SenateSponsorship
from .schema import (
    SponsorListSchema,
    CouncilMemberSponsorshipSchema,
    StateBillSponsorshipsSchema,
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
    if sponsorships and sponsorships[0].sponsor_sequence == 0:
        lead_sponsor = sponsorships[0].person
        sponsorships.pop(0)
    else:
        lead_sponsor = None

    non_sponsors = (
        Person.query.filter(
            Person.id.not_in([s.council_member_id for s in sponsorships])
            & (Person.type == Person.PersonType.COUNCIL_MEMBER)
        )
        .order_by(Person.name)
        .all()
    )
    return SponsorListSchema().jsonify(
        {
            "lead_sponsor": lead_sponsor,
            "cosponsors": [s.person for s in sponsorships],
            "non_sponsors": non_sponsors,
        }
    )


@app.route("/api/state-bills/<uuid:bill_id>/sponsorships", methods=["GET"])
@auth_required
def state_bill_sponsorships(bill_id):
    state_bill = StateBill.query.get(bill_id)
    if not state_bill:
        raise exceptions.NotFound()

    senate_sponsorships = (
        SenateSponsorship.query.filter_by(senate_bill_id=bill_id)
        .options(joinedload(SenateSponsorship.senator))
        .all()
    )
    senate_cosponsors = (s.senator.person for s in senate_sponsorships if not s.is_lead_sponsor)
    senate_lead_sponsor_list = [s.senator.person for s in senate_sponsorships if s.is_lead_sponsor]
    senate_lead_sponsor = senate_lead_sponsor_list[0] if senate_lead_sponsor_list else None
    senate_non_sponsors = Senator.query.filter(
        Senator.person_id.not_in([s.senator_id for s in senate_sponsorships])
    ).all()

    assembly_sponsorships = (
        AssemblySponsorship.query.filter_by(assembly_bill_id=bill_id)
        .options(joinedload(AssemblySponsorship.assembly_member))
        .all()
    )
    assembly_cosponsors = (s.assembly_member.person for s in assembly_sponsorships if not s.is_lead_sponsor)
    assembly_lead_sponsor_list = [s.assembly_member.person for s in assembly_sponsorships if s.is_lead_sponsor]
    assembly_lead_sponsor = assembly_lead_sponsor_list[0] if assembly_lead_sponsor_list else None
    assembly_non_sponsors = AssemblyMember.query.filter(
        AssemblyMember.person_id.not_in(
            [s.assembly_member_id for s in assembly_sponsorships]
        )
    ).all()

    return StateBillSponsorshipsSchema().jsonify(
        {
            "bill_id": bill_id,
            "senate_sponsorships": {
                "lead_sponsor": senate_lead_sponsor,
                "cosponsors": senate_cosponsors,
                "non_sponsors": (s.person for s in senate_non_sponsors),
            },
            "assembly_sponsorships": {
                "lead_sponsor": assembly_lead_sponsor,
                "cosponsors": assembly_cosponsors,
                "non_sponsors": (a.person for a in assembly_non_sponsors),
            }
        }
    )
