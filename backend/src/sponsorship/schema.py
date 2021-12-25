from marshmallow import fields

from ..bill.schema import CityBillSchema
from ..person.schema import PersonSchema
from ..schema import CamelCaseSchema


class CouncilMemberSponsorshipSchema(CamelCaseSchema):
    council_member_id = fields.UUID(required=True)
    bill = fields.Nested(CityBillSchema)


# TODO: Separate out positive and negative sponsors into different types, this gets ugly
class CityBillSponsorshipSchema(CamelCaseSchema):
    bill_id = fields.Integer(required=True)
    person = fields.Nested(PersonSchema)
    is_sponsor = fields.Boolean()
    sponsor_sequence = fields.Integer()



"""
Several options

1. Different schemas for these different conditions.

GET /persons/123 --> {
    name: "Brad Lander",
    type: COUNCIL_MEMBER,
    council_member: {
        borough: "Brooklyn"
    }
}

Then this

GET /city-council-sponsorships/123 --> {
    bill_id: 123,
    person: {
        name: "Brad Lander",
        type: COUNCIL_MEMBER,
        council_member: {
            borough: "Brooklyn"
        }
    }
}
Notes:
- Single interface for Person, which means client can reuse component, and API is consistent
- Single schema for Person as well
- Requires a different join condition in order for the FK to be more specific

OR this:

GET /city-council-sponsorships/123 --> {
    bill_id: 123,
    city_council_member: {
        borough: "Brooklyn",
        person: {
            name: "Brad Lander"
        }
    }
}
Notes:
- Different schemas for each one, which is more complicated
- Simpler join condition

Decision:
- I can do both on the model. Have a double relationship to join with either thing. But keep the consistent interface.



"""