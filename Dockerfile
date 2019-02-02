FROM python:3.7-alpine
MAINTAINER Hassani

# Stop python from buffering output
ENV PYTHONUNBUFFERED 1

# Dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Dir for source code
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a user for the app
RUN adduser -D user
USER user