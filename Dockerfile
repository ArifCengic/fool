FROM python:3.7-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set working directory
WORKDIR /usr/src/app

# install dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt

# copy project
COPY . .

EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT "./docker-entrypoint.sh"
