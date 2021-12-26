from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import TIMESTAMP as _TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as _UUID

from .app import app

db = SQLAlchemy(app)


class UUID(TypeDecorator):
    cache_ok = True

    impl = _UUID(as_uuid=True)


class TIMESTAMP(TypeDecorator):
    impl = _TIMESTAMP(timezone=True)
