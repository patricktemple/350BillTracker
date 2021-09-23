from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import TIMESTAMP as _TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as _UUID

from .app import app

db = SQLAlchemy(app)


class UUID(TypeDecorator):
    impl = _UUID(as_uuid=True)


class TIMESTAMP(TypeDecorator):
    impl = _TIMESTAMP(timezone=True)


class Hello(db.Model):
    __tablename__ = "hello"

    name = Column(Text, primary_key=True)
