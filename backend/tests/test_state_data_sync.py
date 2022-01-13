from src.models import db
from src.state_static_sync import fill_static_state_data

from src.person.models import OfficeContact


def test_state_data_sync(senator, assembly_member):
    fill_static_state_data(
        senate_data_by_member_id={
            senator.senator.state_member_id: {
                "email": "newemail@senate.gov",
                "party": "Senate fake party",
                "albany_contact": [{
                    "phone": "123-456-7890",
                    "city": "Albany",
                    "fax": "123-456-1111",
                }]
                ,
                "district_contact": [],
            },
        },
        assembly_data_by_member_id={
            assembly_member.assembly_member.state_member_id: {
                "email": "newemail@assembly.gov",
                "party": "Assembly fake party",
                "district_contact": [{
                    "phone": "123-456-7890",
                    "city": "Poughkeepsie",
                    "fax": "123-456-1111",
                }],
                "albany_contact": []
            }
        },
    )

    # Test that it commits by rolling back uncommitted changes
    db.session.rollback()

    assert senator.party == "Senate fake party"
    assert senator.email == "newemail@senate.gov"
    assert senator.office_contacts[0].phone == '123-456-7890'
    assert senator.office_contacts[0].city == 'Albany'
    assert senator.office_contacts[0].fax == '123-456-1111'
    assert senator.office_contacts[0].type == OfficeContact.OfficeContactType.CENTRAL_OFFICE

    assert assembly_member.party == "Assembly fake party"
    assert assembly_member.email == "newemail@assembly.gov"
    assert assembly_member.office_contacts[0].fax == '123-456-1111'
    assert assembly_member.office_contacts[0].city == 'Poughkeepsie'
    assert assembly_member.office_contacts[0].type == OfficeContact.OfficeContactType.DISTRICT_OFFICE


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

    # Test that it commits by rolling back uncommitted changes
    db.session.rollback()

    assert senator.email == original_senator_email
    assert assembly_member.email == original_assembly_email
