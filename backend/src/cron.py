import logging
from time import sleep

from .app import app


@app.cli.command("cron")
def cron_command():
    logging.info("Cron job starting")
    while True:
        logging.info("Hello!")

        sleep(5)
