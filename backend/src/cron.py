import logging
from time import sleep

from . import bill_notifications, council_sync, models, state_api
from .app import app
from .settings import ENABLE_CRON


@app.cli.command("cron")
def cron_command():
    # TODO: Refactor to improve error handling
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

                logging.info("Adding state reps")
                state_api.add_state_representatives() # todo exception handling

                # logging.info("Filling state rep static data")
                # state_api.fill_state_representative_static_data()
                # TODO: Update state sponsorships, bill status

                # bill_snapshots = bill_notifications.snapshot_bills()

                # logging.info("Syncing all bill updates")
                # council_sync.sync_bill_updates()

                # logging.info("Syncing all bill sponsorships")
                # council_sync.update_all_sponsorships()

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
