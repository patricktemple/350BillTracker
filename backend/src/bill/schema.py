from marshmallow import fields
from marshmallow_enum import EnumField

from ..schema import CamelCaseSchema
from .models import Bill


class CityBillSchema(CamelCaseSchema):
    file = fields.String(dump_only=True)
    title = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    council_body = fields.String(dump_only=True)
    city_bill_id = fields.Integer(dump_only=True)


class TrackCityBillSchema(CamelCaseSchema):
    city_bill_id = fields.Integer()


class SenateBillVersionSchema(CamelCaseSchema):
    version_name = fields.String(dump_only=True)


class AssemblyBillVersionSchema(CamelCaseSchema):
    version_name = fields.String(dump_only=True)


class StateBillSchema(CamelCaseSchema):
    active_senate_version = fields.Nested(SenateBillVersionSchema)
    active_assembly_version = fields.Nested(AssemblyBillVersionSchema)


class BillSchema(CamelCaseSchema):
    # Data pulled from the API
    id = fields.UUID(dump_only=True)
    name = fields.String(dump_only=True)

    # Data that we track
    tracked = fields.Boolean(dump_only=True)
    notes = fields.String(required=True)
    nickname = fields.String(required=True)
    twitter_search_terms = fields.List(fields.String(), required=True)
    type = EnumField(Bill.BillType, dump_only=True)
    city_bill = fields.Nested(CityBillSchema)
    state_bill = fields.Nested(StateBillSchema)


# Bill attachments ----------------------------------------------------------------------
class BillAttachmentSchema(CamelCaseSchema):
    id = fields.UUID()
    bill_id = fields.UUID()
    name = fields.String()
    url = fields.String()


class PowerHourSchema(CamelCaseSchema):
    id = fields.UUID(dump_only=True)
    power_hour_id_to_import = fields.UUID(load_only=True, missing=None)

    bill_id = fields.Integer(dump_only=True)
    title = fields.String()
    spreadsheet_url = fields.String(dump_only=True)
    created_at = fields.DateTime()


class CreatePowerHourSchema(CamelCaseSchema):
    power_hour = fields.Nested(PowerHourSchema)
    messages = fields.List(fields.String())
