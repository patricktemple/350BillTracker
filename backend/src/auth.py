from functools import wraps

import jwt
from flask import request

from .settings import JWT_SECRET

JWT_ALGORITHM = "HS256"


def create_jwt(user_id):
    # TODO: Experiation time, iat
    # Use this doc: https://auth0.com/docs/security/tokens/json-web-tokens/json-web-token-claims
    payload = {"sub": str(user_id)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token):
    # TODO check expiration time
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# TODO: Rewrite this to invert the auth check
def auth_required(view_fn):
    @wraps(view_fn)
    def check_auth_and_run(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            # TODO: HTTP error types in flask?
            raise ValueError("Authorization required")
        if not auth.startswith("JWT "):
            raise ValueError("Expecting JWT auth type")

        jwt = auth[4:]
        verify_jwt(jwt)

        # TODO: Verify that this user still exists

        return view_fn(*args, **kwargs)

    return check_auth_and_run
