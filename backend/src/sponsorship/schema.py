from marshmallow import fields

from ..bill.schema import BillSchema
from ..person.schema import PersonSchema
from ..schema import CamelCaseSchema


class CouncilMemberSponsorshipSchema(CamelCaseSchema):
    council_member_id = fields.UUID(required=True)
    bill = fields.Nested(BillSchema)


# TODO: Separate out positive and negative sponsors into different types, this gets ugly
class CityBillSponsorshipSchema(CamelCaseSchema):
    bill_id = fields.UUID(required=True)
    person = fields.Nested(PersonSchema)
    is_sponsor = fields.Boolean()
    sponsor_sequence = fields.Integer()
