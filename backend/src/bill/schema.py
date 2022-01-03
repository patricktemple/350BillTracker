from marshmallow import fields
from marshmallow_enum import EnumField

from ..schema import CamelCaseSchema
from .models import Bill, StateChamber


class CityBillSchema(CamelCaseSchema):
    file = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    council_body = fields.String(dump_only=True)
    city_bill_id = fields.Integer(dump_only=True)
    sponsor_count = fields.Integer(dump_only=True)


class TrackCityBillSchema(CamelCaseSchema):
    city_bill_id = fields.Integer()


class StateChamberBillSchema(CamelCaseSchema):
    version_name = fields.String(dump_only=True)
    sponsor_count = fields.Integer(dump_only=True)
    status = fields.String(dump_only=True)
    base_print_no = fields.String(dump_only=True)


class StateBillSchema(CamelCaseSchema):
    senate_bill = fields.Nested(StateChamberBillSchema)
    assembly_bill = fields.Nested(StateChamberBillSchema)


class TrackStateBillSchema(CamelCaseSchema):
    session_year = fields.Integer()
    base_print_no = fields.String()


class BillSchema(CamelCaseSchema):
    # Data pulled from the API
    id = fields.UUID(dump_only=True)
    name = fields.String(dump_only=True)
    description = fields.String(dump_only=True)

    # Derived data from either city or state bill
    status = fields.String(dump_only=True)
    code_name = fields.String(dump_only=True)

    # Data that we track
    tracked = fields.Boolean(dump_only=True)
    notes = fields.String(required=True)
    nickname = fields.String(required=True)
    twitter_search_terms = fields.List(fields.String(), required=True)
    type = EnumField(Bill.BillType, dump_only=True)
    city_bill = fields.Nested(CityBillSchema)
    state_bill = fields.Nested(StateBillSchema)


# class StateBillSearchParamsSchema(CamelCaseSchema):
#     code_name = fields.String(required=True)
#     session_year = fields.String(load_default=None)


class StateBillSearchResultSchema(CamelCaseSchema):
    name = fields.String(dump_only=True)
    description = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    base_print_no = fields.String(dump_only=True)
    session_year = fields.Integer(dump_only=True)
    chamber = EnumField(StateChamber, dump_only=True)
    active_version = fields.String(dump_only=True)
    tracked = fields.Boolean(dump_only=True)
    other_chamber_bill_print_no = fields.String(dump_only=True)


# Bill attachments ----------------------------------------------------------------------
class BillAttachmentSchema(CamelCaseSchema):
    id = fields.UUID()
    bill_id = fields.UUID()
    name = fields.String()
    url = fields.String()


class PowerHourSchema(CamelCaseSchema):
    id = fields.UUID(dump_only=True)
    power_hour_id_to_import = fields.UUID(load_only=True, load_default=None)

    bill_id = fields.Integer(dump_only=True)
    title = fields.String()
    spreadsheet_url = fields.String(dump_only=True)
    created_at = fields.DateTime()


class CreatePowerHourSchema(CamelCaseSchema):
    power_hour = fields.Nested(PowerHourSchema)
    messages = fields.List(fields.String())
