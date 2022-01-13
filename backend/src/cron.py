import logging
from time import sleep

from . import (
    bill_notifications,
    council_sync,
    models,
    state_api,
    state_static_sync,
)
from .app import app
from .settings import ENABLE_CRON
from .static_data import assembly_data, senate_data


@app.cli.command("cron")
def cron_command():
    logging.info("Cron job starting")
    while True:
        if ENABLE_CRON:
            try:
                logging.info("Syncing data...")
                # logging.info("Adding city council members")
                # council_sync.add_council_members()

                # logging.info("Updating city council member contact info")
                # council_sync.fill_council_person_data_from_api()

                # logging.info("Refreshing city council_member_static_data")
                # # TODO: This doesn't need to run at cron time though! Just once on startup
                # council_sync.fill_council_person_static_data()

                logging.info("Syncing state reps")
                state_api.sync_state_representatives()

                # bill_snapshots = bill_notifications.snapshot_bills()

                logging.info("Syncing state bill updates")
                state_api.update_state_bills()

                logging.info("Syncing all city bill updates")
                council_sync.sync_bill_updates()

                logging.info("Syncing all city bill sponsorships")
                council_sync.update_all_sponsorships()

                state_static_sync.fill_static_state_data()

                # logging.info(
                #     "Checking if bills have changed, and sending notifications if so"
                # )
                # bill_notifications.send_bill_update_notifications(
                #     bill_snapshots
                # )

                logging.info("Cron run complete")
            except Exception as e:
                logging.exception(e)
                logging.error("Unhandled exception during cron run")
                models.db.session.rollback()
        else:
            logging.info("Cron job is disabled, it won't do anything")

        sleep(60 * 60)
