FROM python:3.9

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt ./
COPY alembic.ini ./

RUN pip install -r requirements.txt

# Bundle app source
COPY /src /app/src
COPY /alembic /app/alembic
COPY /script_deployed /app/script_deployed
COPY /__frontend_build__/index.html /app/src/templates/index.html
COPY /__frontend_build__/static /app/src/static

EXPOSE 5000
ENV FLASK_APP=src.app
CMD [ "flask", "run", "--host=0.0.0.0" ]