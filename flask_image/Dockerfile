FROM ubuntu:18.04
MAINTAINER Esteban Buz "esteban.buz@gmail.com"

RUN apt-get update && apt-get install -y libpq-dev python3-pip python3-dev build-essential wait-for-it

WORKDIR /app
COPY ./flask_app/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
#COPY ./flask_app /app

ENV FLASK_APP=plant_finder/__init__.py
ENV FLASK_ENV=development
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 5000
