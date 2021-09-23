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

EXPOSE 5000
CMD [ "flask", "run", "--host=0.0.0.0" ]
