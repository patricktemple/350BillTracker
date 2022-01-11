from src.models import db
from src.state_static_sync import fill_static_state_data


def test_state_data_sync(senator, assembly_member):
    fill_static_state_data(
        senate_data_by_member_id={
            senator.senator.state_member_id: {
                "email": "newemail@senate.gov",
                "party": "Senate fake party",
            },
        },
        assembly_data_by_member_id={
            assembly_member.assembly_member.state_member_id: {
                "email": "newemail@assembly.gov",
                "party": "Assembly fake party",
            }
        },
    )

    # Test that it commits
    db.session.expire(senator)
    db.session.expire(assembly_member)

    assert senator.party == "Senate fake party"
    assert senator.email == "newemail@senate.gov"
    assert assembly_member.party == "Assembly fake party"
    assert assembly_member.email == "newemail@assembly.gov"


def test_state_data_sync__not_found(senator, assembly_member):
    original_senator_email = senator.email
    original_assembly_email = assembly_member.email
    fill_static_state_data(
        senate_data_by_member_id={
            70: {"email": "newemail@senate.gov", "party": "Senate fake party"},
        },
        assembly_data_by_member_id={
            80: {
                "email": "newemail@assembly.gov",
                "party": "Assembly fake party",
            }
        },
    )

    # Test that it commits
    db.session.expire(senator)
    db.session.expire(assembly_member)

    assert senator.email == original_senator_email
    assert assembly_member.email == original_assembly_email
