import json

from flask.testing import FlaskClient

from src.auth import create_jwt


class ApiClient(FlaskClient):
    authenticated_user_id = None

    def set_authenticated_user_id(self, user_id):
        self.authenticated_user_id = user_id

    def open(self, path, *args, headers=None, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        if kwargs["content_type"] == "application/json" and "data" in kwargs:
            kwargs["data"] = json.dumps(kwargs["data"])

        headers = {} if headers is None else headers.copy()
        if self.authenticated_user_id:
            headers[
                "Authorization"
            ] = f"JWT {create_jwt(self.authenticated_user_id)}"

        return super().open(path, *args, headers=headers, **kwargs)


def assert_response(response, status_code, data):
    assert response.status_code == status_code

    json_data = get_response_data(response)
    assert json_data == data, f"Expected: {data}\n\nActual: {json_data}"


def get_response_data(response):
    return json.loads(response.data)
