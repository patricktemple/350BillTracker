import logging
from time import sleep

from . import bill_notifications, council_sync, models
from .app import app
from .settings import ENABLE_CRON


@app.cli.command("cron")
def cron_command():
    # TODO: Refactor to improve error handling
    logging.info("Cron job starting")
    while True:
        if ENABLE_CRON:
            try:
                # logging.info("Syncing data...")
                # logging.info("Adding council members")
                # council_sync.add_council_members()

                # logging.info("Updating council member contact info")
                # council_sync.fill_council_person_data_from_api()

                # logging.info("Refreshing council_member_static_data")
                # This doesn't need to run at cron time though! Just once on startup
                # council_sync.fill_council_person_static_data()

                bill_snapshots = bill_notifications.snapshot_bills()

                logging.info("Syncing all bill updates")
                council_sync.sync_bill_updates()

                logging.info("Syncing all bill sponsorships")
                council_sync.update_all_sponsorships()

                logging.info(
                    "Checking if bills have changed, and sending notifications if so"
                )
                bill_notifications.send_bill_update_notifications(
                    bill_snapshots
                )

                logging.info("Cron run complete")
            except Exception as e:
                logging.exception(e)
                logging.error("Unhandled exception during cron run")
                models.db.session.rollback()
        else:
            logging.info("Cron job is disabled, it won't do anything")

        # TODO: Revert this!
        sleep(1 * 60)
