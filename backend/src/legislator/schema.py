from marshmallow import fields

from ..schema import CamelCaseSchema


class LegislatorSchema(CamelCaseSchema):
    # Data synced from the API
    name = fields.String(dump_only=True)
    id = fields.Integer(dump_only=True)
    term_start = fields.DateTime(dump_only=True)
    term_end = fields.DateTime(dump_only=True)
    email = fields.String(dump_only=True)
    district_phone = fields.String(dump_only=True)
    legislative_phone = fields.String(dump_only=True)
    borough = fields.String(dump_only=True)
    website = fields.String(dump_only=True)

    # Static data that we add in
    twitter = fields.String(dump_only=True)

    # TODO: Make this an enum!
    party = fields.String(dump_only=True)

    # Extra data we track
    notes = fields.String(missing=None)


class StafferSchema(CamelCaseSchema):
    id = fields.UUID()
    name = fields.String()
    title = fields.String(missing=None)
    email = fields.Email(missing=None)
    phone = fields.String(missing=None)
    twitter = fields.String(missing=None)
    # TODO: Move twitter validation into schema
