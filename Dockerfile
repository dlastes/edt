FROM python:3

# see output in our console 
ENV PYTHONUNBUFFERED 1
ARG CONFIG

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/requirements /code/requirements/
RUN pip install --no-cache-dir -r /code/requirements/$CONFIG.txt

COPY . /code/