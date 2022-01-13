from .models import db
from .person.models import AssemblyMember, Person, Senator, OfficeContact
from .static_data import assembly_data, senate_data


from .person.models import AssemblyMember, Senator
from .utils import cron_function


def _fill_person_static_data(assembly_member_or_senator, static_data_set):
    static_data = static_data_set.get(
        assembly_member_or_senator.state_member_id
    )
    if static_data:
        assembly_member_or_senator.person.party = static_data.get("party")
        assembly_member_or_senator.person.email = static_data.get("email")
        assembly_member_or_senator.person.office_contacts.clear()

        for office in static_data['district_contact']:
            # This just keeps duplicating the info...
            assembly_member_or_senator.person.office_contacts.append(OfficeContact(
                city=office.get('city'),
                phone=office.get('phone'),
                fax=office.get('fax'),
                type=OfficeContact.OfficeContactType.DISTRICT_OFFICE,
            ))
        for office in static_data['albany_contact']:
            assembly_member_or_senator.person.office_contacts.append(OfficeContact(
                city=office.get('city'),
                phone=office.get('phone'),
                fax=office.get('fax'),
                type=OfficeContact.OfficeContactType.CENTRAL_OFFICE,
            ))


@cron_function
def fill_static_state_data(
    *, senate_data_by_member_id, assembly_data_by_member_id
):
    senators = Senator.query.all()
    for senator in senators:
        _fill_person_static_data(senator, senate_data_by_member_id)

    assembly_members = AssemblyMember.query.all()
    for assembly_member in assembly_members:
        _fill_person_static_data(assembly_member, assembly_data_by_member_id)

    db.session.commit()
