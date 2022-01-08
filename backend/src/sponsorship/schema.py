from marshmallow import fields

from ..bill.schema import BillSchema
from ..person.schema import PersonSchema
from ..schema import CamelCaseSchema


class CouncilMemberSponsorshipSchema(CamelCaseSchema):
    council_member_id = fields.UUID(required=True)
    bill = fields.Nested(BillSchema)


class SponsorListSchema(CamelCaseSchema):
    # i like this because we will likely want to show lead sponsor more prominently in places
    # so it's nice to have its own field like that
    lead_sponsor = fields.Nested(PersonSchema)
    cosponsors = fields.List(fields.Nested(PersonSchema))
    non_sponsors = fields.List(fields.Nested(PersonSchema))


class StateBillSponsorshipsSchema(CamelCaseSchema):
    senate_sponsorships = fields.Nested(SponsorListSchema)
    assembly_sponsorships = fields.Nested(SponsorListSchema)


# As I fix this lead sponsor issue, should really take the time to unify the two representations of sponsorships here too.
