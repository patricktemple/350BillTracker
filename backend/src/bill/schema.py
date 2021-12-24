from marshmallow import fields

from ..schema import CamelCaseSchema


class BillSchema(CamelCaseSchema):
    # Data pulled from the API
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    title = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    body = fields.String(dump_only=True)
    file = fields.String(dump_only=True)

    # Data that we track
    tracked = fields.Boolean(dump_only=True)
    notes = fields.String(required=True)
    nickname = fields.String(required=True)
    twitter_search_terms = fields.List(fields.String(), required=True)


# Bill attachments ----------------------------------------------------------------------
class BillAttachmentSchema(CamelCaseSchema):
    id = fields.Integer()
    bill_id = fields.Integer()
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
