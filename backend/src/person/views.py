import re

from flask import jsonify, request
from sqlalchemy.orm import joinedload
from werkzeug import exceptions

from ..app import app
from ..auth import auth_required
from ..models import db
from .models import (
    CouncilCommittee,
    CouncilCommitteeMembership,
    OfficeContact,
    Person,
    Staffer,
)
from .schema import (
    CouncilCommitteeSchema,
    CouncilMemberCommitteeMembershipSchema,
    CreateStafferSchema,
    OfficeContactSchema,
    PersonSchema,
    PersonWithContactsSchema,
)


@app.route("/api/persons", methods=["GET"])
@auth_required
def get_persons():
    persons = Person.query.order_by(Person.name).all()
    return PersonSchema(many=True).jsonify(persons)


@app.route("/api/persons/<uuid:person_id>", methods=["PUT"])
@auth_required
def update_legislator(person_id):
    data = PersonSchema().load(request.json)

    person = Person.query.get(person_id)
    person.notes = data["notes"]

    db.session.commit()

    return jsonify({})


@app.route("/api/persons/<uuid:person_id>/staffers", methods=["GET"])
@auth_required
def person_staffers(person_id):
    person = Person.query.get(person_id)

    return PersonWithContactsSchema(many=True).jsonify(person.staffer_persons)


@app.route("/api/persons/<uuid:person_id>/staffers", methods=["POST"])
@auth_required
def add_person_staffer(person_id):
    data = CreateStafferSchema().load(request.json)
    twitter = data["twitter"]
    if twitter:
        if twitter.startswith("@"):
            twitter = twitter[1:]
        pattern = re.compile("^[A-Za-z0-9_]{1,15}$")
        if not pattern.match(twitter):
            raise exceptions.UnprocessableEntity(f"Invalid Twitter: {twitter}")

    staffer_person = Person(
        name=data["name"],
        title=data["title"],
        email=data["email"],
        twitter=twitter,
        type=Person.PersonType.STAFFER,
    )
    staffer_person.office_contacts.append(
        OfficeContact(
            type=OfficeContact.OfficeContactType.OTHER, phone=data["phone"]
        )
    )
    staffer_person.staffer = Staffer(
        boss_id=person_id,
    )
    db.session.add(staffer_person)
    db.session.commit()

    # TODO: Return the object in all Creates, to be consistent
    return jsonify({})


@app.route("/api/persons/-/staffers/<uuid:staffer_id>", methods=["DELETE"])
@auth_required
def delete_staffer(staffer_id):
    staffer = Staffer.query.get(staffer_id)
    if not staffer:
        raise exceptions.NotFound()
    db.session.delete(staffer.person)
    db.session.commit()

    # TODO: Return the object in all Creates, to be consistent
    return jsonify({})


@app.route("/api/persons/<uuid:person_id>/contacts", methods=["GET"])
@auth_required
def get_contacts(person_id):
    contacts = (
        OfficeContact.query.filter_by(person_id=person_id)
        .order_by(OfficeContact.type)
        .all()
    )
    return OfficeContactSchema(many=True).jsonify(contacts)


@app.route("/api/council-members/<uuid:person_id>/committees", methods=["GET"])
@auth_required
def get_council_member_committees(person_id):
    committee_memberships = (
        CouncilCommitteeMembership.query.filter_by(person_id=person_id)
        .join(CouncilCommitteeMembership.committee)
        .order_by(CouncilCommittee.name)
        .all()
    )
    return CouncilMemberCommitteeMembershipSchema(many=True).jsonify(
        committee_memberships
    )


# TODO test this
