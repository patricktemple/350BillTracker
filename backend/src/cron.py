import logging
from time import sleep

from .app import app
from . import council_sync


@app.cli.command("cron")
def cron_command():
    logging.info("Cron job starting")
    while True:
        logging.info("Syncing data...")

        logging.info("Adding council members")
        council_sync.add_council_members()

        logging.info("Updating council member contact info")
        council_sync.fill_council_person_data()

        logging.info("Syncing all bill sponsorships")
        # TODO: Also update the bill itself, to get new status for example
        council_sync.update_all_sponsorships()

        sleep(60 * 60)
