#!/bin/bash

# set -euo pipefail

# # EB has not yet built the image via docker compose, so if we try to reference it here, it will use the previous one
# docker build ../../../var/app/staging -t legislation_app
# echo "About to run migration"

# # this .env is the auto-inserted one by beanstalk, not any local one (which isn't in git repo anyway)
# docker run --env-file=../../../var/app/staging/.env --entrypoint alembic legislation_app upgrade head 2>&1
# echo "Migration done"