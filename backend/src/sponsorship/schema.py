from marshmallow import fields

from ..bill.schema import BillSchema
from ..person.schema import PersonSchema
from ..schema import CamelCaseSchema


class CouncilMemberSponsorshipSchema(CamelCaseSchema):
    council_member_id = fields.UUID(required=True)
    bill = fields.Nested(BillSchema)


class SponsorListSchema(CamelCaseSchema):
    lead_sponsor = fields.Nested(PersonSchema)
    cosponsors = fields.List(fields.Nested(PersonSchema))
    non_sponsors = fields.List(fields.Nested(PersonSchema))


class StateBillSponsorshipsSchema(CamelCaseSchema):
    senate_sponsorships = fields.Nested(SponsorListSchema)
    assembly_sponsorships = fields.Nested(SponsorListSchema)


class StateRepresenativeSponsorshipSchema(CamelCaseSchema):
    person_id = fields.UUID(required=True)
    bill = fields.Nested(BillSchema)
