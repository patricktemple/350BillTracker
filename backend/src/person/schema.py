from marshmallow import fields

from ..schema import CamelCaseSchema


class PersonSchema(CamelCaseSchema):
    # Data synced from the API
    name = fields.String(dump_only=True)
    id = fields.Integer(dump_only=True)

    email = fields.String(dump_only=True)
    phone = fields.String(dump_only=True)

    # Static data that we add in
    twitter = fields.String(dump_only=True)

    type = fields.String(dump_only=True) # TODO enum!!!

    # TODO: Make this an enum!
## unclear which level this goes into

    # Extra data we track
    notes = fields.String(missing=None)

    title = fields.String(missing=None)

    party = fields.String(dump_only=True)  # TODO this is now an enum

    # TODO: Work through these:
    council_member = fields.Nested(CouncilMemberSchema)
    senator = fields.Nested(SenatorSchema)
    assembly_member = fields.Nested(AssemblyMemberSchema)


class CouncilMemberSchema(CamelCaseSchema):
    term_start = fields.DateTime(dump_only=True)
    term_end = fields.DateTime(dump_only=True)
    borough = fields.String(dump_only=True)
    website = fields.String(dump_only=True)
    legislative_phone = fields.String(dump_only=True)


# I'm not actually sure we'll  need these schemas:
class SenatorSchema(CamelCaseSchema):
    person = fields.Nested(PersonSchema)

class AssemblyMemberSchema(CamelCaseSchema):
    person = fields.Nested(PersonSchema)


class StafferSchema(CamelCaseSchema):
    person = fields.Nested(PersonSchema)