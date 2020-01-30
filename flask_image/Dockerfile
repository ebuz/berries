FROM ubuntu:18.04
MAINTAINER Esteban Buz "esteban.buz@gmail.com"

RUN apt-get update && apt-get install -y libpq-dev python3-pip python3-dev build-essential wait-for-it

WORKDIR /app
COPY ./flask_app/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
#COPY ./flask_app /app

ARG FLASK_APP=plant_finder
ARG FLASK_ENV=development
EXPOSE 5000
