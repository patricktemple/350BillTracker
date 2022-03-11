import logging
import secrets
from datetime import timedelta

import flask
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required, create_jwt
from ..bill.models import Bill, UserBillSettings
from ..models import db
from ..ses import send_login_link_email
from ..settings import APP_ORIGIN
from ..utils import now
from .models import LoginLink, User
from .schema import (
    CreateLoginLinkSchema,
    LoginSchema,
    UserBillSettingsSchema,
    UserSchema,
)


@app.route(
    "/api/create-login-link",
    methods=["POST"],
)
def create_login_link():
    data = CreateLoginLinkSchema().load(request.json)

    email_lower = data["email"].lower()
    user = User.query.filter_by(email=email_lower).one_or_none()
    if not user:
        raise exceptions.UnprocessableEntity("user not found")

    login = LoginLink(
        user_id=user.id,
        expires_at=now() + timedelta(days=1),
        token=secrets.token_urlsafe(),
    )
    db.session.add(login)
    db.session.commit()

    send_login_link_email(
        email_lower, f"{APP_ORIGIN}/login?token={login.token}"
    )

    return jsonify({})


@app.route(
    "/api/login",
    methods=["POST"],
)
def login():
    data = LoginSchema().load(request.json)
    token = data["token"]

    login_link = (
        LoginLink.query.filter_by(token=token).with_for_update().one_or_none()
    )

    # TODO: Pass a message down to the client distinguishing these 403s
    error_code = None
    if not login_link:
        error_code = "invalidLink"
    elif login_link.expires_at < now():
        error_code = "linkExpired"
    elif login_link.used_at:
        error_code = "alreadyUsed"

    if error_code:
        return jsonify({"errorCode": error_code}), 401

    login_link.used_at = now()
    db.session.commit()

    user_id = login_link.user_id
    return jsonify({"authToken": create_jwt(user_id)})


# TODO: Add assertions on error messages!


@app.route(
    "/api/users",
    methods=["GET"],
)
@auth_required
def list_users():
    users = User.query.all()

    return UserSchema(many=True).jsonify(users)


@app.route(
    "/api/users/<uuid:user_id>",
    methods=["DELETE"],
)
@auth_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user.can_be_deleted:
        raise exceptions.UnprocessableEntity()
    db.session.delete(user)
    db.session.commit()

    return jsonify({})


@app.route(
    "/api/users",
    methods=["POST"],
)
@auth_required
def create_user():
    data = UserSchema().load(request.json)
    user = User(name=data["name"], email=data["email"].lower())
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        raise exceptions.UnprocessableEntity(
            "User already exists with this email"
        )

    return jsonify({})


@app.route(
    "/api/viewer",
    methods=["GET"],
)
@auth_required
def get_current_user():
    current_user = User.query.get(flask.g.request_user_id)

    return UserSchema().jsonify(current_user)


@app.route(
    "/api/viewer",
    methods=["PUT"],
)
@auth_required
def update_current_user():
    data = UserSchema().load(request.json)

    current_user = User.query.get(flask.g.request_user_id)
    current_user.send_bill_update_notifications = data[
        "send_bill_update_notifications"
    ]
    db.session.commit()

    return jsonify({})


@app.route(
    "/api/viewer/bill-settings",
    methods=["GET"],
)
@auth_required
def get_viewer_bill_settings():
    bills = Bill.query.all()

    complete_bill_settings = []
    for bill in bills:
        viewer_bill_settings = bill.viewer_settings
        if viewer_bill_settings:
            complete_bill_settings.append(viewer_bill_settings)
        else:
            complete_bill_settings.append(
                {
                    "bill": bill,
                    "send_bill_update_notifications": False,
                }
            )

    return UserBillSettingsSchema(many=True).jsonify(complete_bill_settings)
