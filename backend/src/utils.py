import logging
from datetime import datetime, timezone

from src.models import db


def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def cron_function(func):
    def impl(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            db.session.rollback()
            logging.exception("Exception thrown during cron function")

    return impl
