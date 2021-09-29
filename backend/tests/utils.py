import json


def assert_response(response, status_code, data):
    assert response.status_code == status_code

    json_data = json.loads(response.data)
    assert json_data == data, f"Expected: {data}\n\nActual: {json_data}"
