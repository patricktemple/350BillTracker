from werkzeug.datastructures import Authorization

from .models import db
from .person.models import AssemblyMember, Person, Senator, OfficeContact
from .static_data import assembly_data, senate_data


def fill_static_state_data():
    senators = Senator.query.all()
    for senator in senators:
        static_data = senate_data.SCRAPED_SENATE_DATA_BY_MEMBER_ID[
            senator.state_member_id
        ]
        if static_data:
            senator.person.party = static_data.get("party")
            senator.person.email = static_data.get("email")

            for office in static_data['district_contact']:
                senator.person.office_contacts.add(OfficeContact(
                    city=office.get('city'),
                    phone=office.get('phone'),
                    fax=office.get('fax') # And maybe contact type?
                ))

    assembly_members = AssemblyMember.query.all()
    for assembly_member in assembly_members:
        static_data = assembly_data.SCRAPED_ASSEMBLY_DATA_BY_MEMBER_ID[
            assembly_member.state_member_id
        ]
        if static_data:
            assembly_member.person.party = static_data.get("party")
            assembly_member.person.email = static_data.get("email")

    db.session.commit()
