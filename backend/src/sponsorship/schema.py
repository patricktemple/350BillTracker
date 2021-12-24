from marshmallow import fields

from ..bill.schema import BillSchema
from ..person.schema import LegislatorSchema
from ..schema import CamelCaseSchema


class SingleMemberSponsorshipsSchema(CamelCaseSchema):
    legislator_id = fields.Integer(required=True)
    bill = fields.Nested(BillSchema)


# TODO: Separate out positive and negative sponsors into different types, this gets ugly
class BillSponsorshipSchema(CamelCaseSchema):
    bill_id = fields.Integer(required=True)
    legislator = fields.Nested(LegislatorSchema)
    is_sponsor = fields.Boolean()
    sponsor_sequence = fields.Integer()
