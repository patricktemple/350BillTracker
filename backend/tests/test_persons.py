from .utils import get_response_data


def test_get_persons(
    client, council_member, senator, assembly_member, senate_staffer, snapshot
):
    response = client.get("/api/persons")

    assert get_response_data(response) == snapshot


def test_get_contacts(client, senator, snapshot):
    response = client.get(f"/api/persons/{str(senator.id)}/contacts")

    assert get_response_data(response) == snapshot
