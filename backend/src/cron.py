import logging
from time import sleep

from . import council_sync
from .app import app
from .settings import ENABLE_CRON


@app.cli.command("cron")
def cron_command():
    # TODO: Refactor to improve error handling
    logging.info("Cron job starting")
    while True:
        if ENABLE_CRON:
            logging.info("Syncing data...")
            logging.info("Adding council members")
            council_sync.add_council_members()

            logging.info("Updating council member contact info")
            council_sync.fill_council_person_data()

            logging.info("Syncing all bill updates")
            council_sync.sync_bill_updates()

            logging.info("Syncing all bill sponsorships")
            # TODO: Also update the bill itself, to get new status for example
            council_sync.update_all_sponsorships()
            logging.info("Cron run complete")
        else:
            logging.info("Cron job is disabled, it won't do anything")

        sleep(60 * 60)
