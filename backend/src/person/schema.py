from marshmallow import fields
from marshmallow_enum import EnumField

from ..schema import CamelCaseSchema
from .models import Person


class CouncilMemberSchema(CamelCaseSchema):
    term_start = fields.DateTime(dump_only=True)
    term_end = fields.DateTime(dump_only=True)
    borough = fields.String(dump_only=True)
    website = fields.String(dump_only=True)
    legislative_phone = fields.String(dump_only=True)


# I'm not actually sure we'll need these schemas yet:
class SenatorSchema(CamelCaseSchema):
    pass


class AssemblyMemberSchema(CamelCaseSchema):
    pass


class CreateStafferSchema(CamelCaseSchema):
    name = fields.String()
    phone = fields.String(missing=None)
    email = fields.String(missing=None)
    twitter = fields.String(missing=None)
    title = fields.String(missing=None)


class PersonSchema(CamelCaseSchema):
    # Data synced from the API
    name = fields.String(dump_only=True)
    id = fields.UUID(dump_only=True)

    email = fields.String(dump_only=True)
    phone = fields.String(dump_only=True)

    # Static data that we add in
    twitter = fields.String(dump_only=True)

    type = EnumField(Person.PersonType)  # dump_only?

    # Extra data we track
    notes = fields.String(missing=None)

    title = fields.String(missing=None)

    party = fields.String(dump_only=True)  # TODO this is now an enum

    # TODO: Work through these:
    council_member = fields.Nested(CouncilMemberSchema)
    senator = fields.Nested(SenatorSchema)
    assembly_member = fields.Nested(AssemblyMemberSchema)
