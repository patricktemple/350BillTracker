import json

from flask.testing import FlaskClient


class ApiClient(FlaskClient):
    def open(self, path, *args, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        if kwargs["content_type"] == "application/json" and "data" in kwargs:
            kwargs["data"] = json.dumps(kwargs["data"])

        return super().open(path, *args, **kwargs)


def assert_response(response, status_code, data):
    assert response.status_code == status_code

    json_data = json.loads(response.data)
    assert json_data == data, f"Expected: {data}\n\nActual: {json_data}"
