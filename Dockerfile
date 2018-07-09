FROM python:3

# see output in our console
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN apt-get update
RUN apt-get -y install memcached

COPY requirements.txt /code/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /code/

