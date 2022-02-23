from marshmallow import fields

from ..schema import CamelCaseSchema
from ..bill.schema import BillSchema


class UserSchema(CamelCaseSchema):
    id = fields.UUID()

    # TODO: On client side, handle email validation failure
    email = fields.Email()
    name = fields.String()
    can_be_deleted = fields.Boolean(dump_only=True)
    send_bill_update_notifications = fields.Boolean()
    

# i can either put this into the user schema on its own... since it gets loaded when the page loads
# or else make it a separate call
# chattiness isn't really a problem due to low scale
# it's a little cleaner to have it be a separate API, so let's do that


class CreateLoginLinkSchema(CamelCaseSchema):
    email = fields.String()


class LoginSchema(CamelCaseSchema):
    token = fields.String()


class UserBillSettingsSchema(CamelCaseSchema):
    bill = fields.Nested(BillSchema)
    send_bill_update_notifications = fields.Boolean()