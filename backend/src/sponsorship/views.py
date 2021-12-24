from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required
from ..bill.models import Bill
from ..legislator.models import Legislator
from ..models import db
from .models import BillSponsorship
from .schema import BillSponsorshipSchema, SingleMemberSponsorshipsSchema


@app.route(
    "/api/legislators/<int:legislator_id>/sponsorships", methods=["GET"]
)
@auth_required
def legislator_sponsorships(legislator_id):
    sponsorships = (
        BillSponsorship.query.filter_by(legislator_id=legislator_id)
        .options(joinedload(BillSponsorship.bill))
        .all()
    )
    return SingleMemberSponsorshipsSchema(many=True).jsonify(sponsorships)


@app.route("/api/saved-bills/<int:bill_id>/sponsorships", methods=["GET"])
@auth_required
def bill_sponsorships(bill_id):
    bill = Bill.query.get(bill_id)
    if not bill:
        raise exceptions.NotFound()
    sponsorships = (
        BillSponsorship.query.filter_by(bill_id=bill_id)
        .options(joinedload(BillSponsorship.legislator))
        .order_by(BillSponsorship.sponsor_sequence)
        .all()
    )
    for sponsorship in sponsorships:
        # This is not a field on the SQLA object, but we set it so that it gets
        # serialized into the response.
        sponsorship.is_sponsor = True

    non_sponsors = (
        Legislator.query.filter(
            Legislator.id.not_in([s.legislator_id for s in sponsorships])
        )
        .order_by(Legislator.name)
        .all()
    )
    non_sponsorships = [
        {
            "bill_id": bill_id,
            "is_sponsor": False,
            "legislator": legislator,
        }
        for legislator in non_sponsors
    ]
    return BillSponsorshipSchema(many=True).jsonify(
        sponsorships + non_sponsorships
    )
