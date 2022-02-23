import secrets
from datetime import timedelta

import flask
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions
import logging

from ..app import app
from ..auth import auth_required, create_jwt
from ..models import db
from ..ses import send_login_link_email
from ..settings import APP_ORIGIN
from ..utils import now
from .models import LoginLink, User
from .schema import CreateLoginLinkSchema, LoginSchema, UserSchema, UserBillSettingsSchema
from ..bill.models import UserBillSettings, Bill


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

    login_link = LoginLink.query.filter_by(token=token).one_or_none()
    if not login_link:
        raise exceptions.Unauthorized()

    user_id = login_link.user_id

    if login_link.expires_at < now():
        raise exceptions.Unauthorized()

    return jsonify({"authToken": create_jwt(user_id)})


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
    # viewer_bill_settings = UserBillSettings.query.filter_by(user_id=flask.g.request_user_id).all()
    bills = Bill.query.all()

    complete_bill_settings = []
    for bill in bills:
        viewer_bill_settings = bill.viewer_settings
        if viewer_bill_settings:
            complete_bill_settings.append(viewer_bill_settings)
        else:
            complete_bill_settings.append({
                "bill": bill,
                "send_bill_update_notifications": False,
            })

    return UserBillSettingsSchema(many=True).jsonify(complete_bill_settings)