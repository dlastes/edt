FROM python:3

# see output in our console 
ENV PYTHONUNBUFFERED 1
ARG CONFIG

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements /code/requirements/
RUN pip install --no-cache-dir -r requirements/requirements.$CONFIG.txt

COPY . /code/