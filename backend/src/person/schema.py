from marshmallow import fields
from marshmallow_enum import EnumField

from ..schema import CamelCaseSchema
from .models import OfficeContact, Person


class OfficeContactSchema(CamelCaseSchema):
    phone = fields.String(dump_only=True)
    fax = fields.String(dump_only=True)
    city = fields.String(dump_only=True)
    type = EnumField(OfficeContact.OfficeContactType, dump_only=True)


class CouncilMemberSchema(CamelCaseSchema):
    term_start = fields.DateTime(dump_only=True)
    term_end = fields.DateTime(dump_only=True)
    borough = fields.String(dump_only=True)
    website = fields.String(dump_only=True)


class SenatorSchema(CamelCaseSchema):
    website = fields.String(dump_only=True)
    district = fields.Integer(dump_only=True)


class AssemblyMemberSchema(CamelCaseSchema):
    website = fields.String(dump_only=True)
    district = fields.Integer(dump_only=True)


class CreateStafferSchema(CamelCaseSchema):
    name = fields.String()
    phone = fields.String(load_default=None)
    email = fields.String(load_default=None)
    twitter = fields.String(load_default=None)
    title = fields.String(load_default=None)


class PersonSchema(CamelCaseSchema):
    # Data synced from the API
    name = fields.String(dump_only=True)
    id = fields.UUID(dump_only=True)

    email = fields.String(dump_only=True)

    # Static data that we add in
    twitter = fields.String(dump_only=True)

    type = EnumField(Person.PersonType, dump_only=True)

    # Extra data we track
    notes = fields.String(load_default=None)

    title = fields.String(load_default=None)

    party = fields.String(dump_only=True)

    council_member = fields.Nested(CouncilMemberSchema)
    senator = fields.Nested(SenatorSchema)
    assembly_member = fields.Nested(AssemblyMemberSchema)


class PersonWithContactsSchema(PersonSchema):
    office_contacts = fields.List(fields.Nested(OfficeContactSchema))