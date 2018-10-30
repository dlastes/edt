FROM python:3

# see output in our console 
ENV PYTHONUNBUFFERED 1
ARG CONFIG

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get -y install memcached

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/requirements /code/requirements/
RUN pip install --no-cache-dir -r /code/requirements/$CONFIG.txt

COPY . /code/