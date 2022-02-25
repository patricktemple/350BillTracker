from marshmallow import fields

from ..bill.schema import BillSchema
from ..schema import CamelCaseSchema


class UserSchema(CamelCaseSchema):
    id = fields.UUID()

    # TODO: On client side, handle email validation failure
    email = fields.Email()
    name = fields.String()
    can_be_deleted = fields.Boolean(dump_only=True)


class CreateLoginLinkSchema(CamelCaseSchema):
    email = fields.String()


class LoginSchema(CamelCaseSchema):
    token = fields.String()


class UserBillSettingsSchema(CamelCaseSchema):
    bill = fields.Nested(BillSchema)
    send_bill_update_notifications = fields.Boolean()
