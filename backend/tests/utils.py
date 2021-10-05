import json

from flask.testing import FlaskClient
import jwt
from src.auth import create_jwt
from uuid import uuid4


class ApiClient(FlaskClient):
    authenticated_user_id = uuid4()

    # def __init__(self, *, authenticated_user_id=None, **kwargs):
    #     self.authenticated_user_id = authenticated_user_id
    #     super(**kwargs)

    def open(self, path, *args, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        if kwargs["content_type"] == "application/json" and "data" in kwargs:
            kwargs["data"] = json.dumps(kwargs["data"])
        if self.authenticated_user_id:
            kwargs["Authorization"] = f"JWT {create_jwt(self.authenticated_user_id)}"

        return super().open(path, *args, **kwargs)


def assert_response(response, status_code, data):
    assert response.status_code == status_code

    json_data = json.loads(response.data)
    assert json_data == data, f"Expected: {data}\n\nActual: {json_data}"
