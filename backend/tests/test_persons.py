from .utils import get_response_data


def test_get_persons(
    client, council_member, senator, assembly_member, senate_staffer, snapshot
):
    response = client.get("/api/persons")

    assert get_response_data(response) == snapshot
