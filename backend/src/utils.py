import logging
from datetime import datetime, timezone
from functools import wraps

from src.models import db


def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def cron_function(func):
    """Wrapper for all top-level functions run inside the cron to ensure that
    errors are cleaned up and a failure in one function does not affect others."""

    @wraps(func)
    def impl(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            db.session.rollback()
            logging.exception("Exception thrown during cron function")

    return impl
