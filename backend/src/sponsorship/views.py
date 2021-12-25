from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required
from ..bill.models import Bill, CityBill
from ..person.models import Person
from ..models import db
from .models import CitySponsorship
from .schema import CityBillSponsorshipSchema, CouncilMemberSponsorshipSchema


@app.route(
    "/api/council-members/<uuid:council_member_id>/sponsorships", methods=["GET"]
)
@auth_required
def council_member_sponsorships(council_member_id):
    sponsorships = (
        CitySponsorship.query.filter_by(council_member_id=council_member_id)
        .options(joinedload(CitySponsorship.bill))
        .all()
    )
    return CouncilMemberSponsorshipSchema(many=True).jsonify(sponsorships)


@app.route("/api/city-bills/<int:bill_id>/sponsorships", methods=["GET"])
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
            Person.id.not_in([s.council_member_id for s in sponsorships]) & (Person.type == Person.PersonType.COUNCIL_MEMBER)
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
