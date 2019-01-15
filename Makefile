#!/usr/bin/make -f

# get the current git branch name
BRANCH := $(shell git branch 2>/dev/null | grep '^*' | colrm 1 2)
CONFIG ?= development
COMPOSE_PROJECT_NAME:=$(shell echo $(CONFIG) | head -c 3)

export CONFIG
export BRANCH
export COMPOSE_PROJECT_NAME

# initialize database with basic datas contained 
# in dump.json for tests purposes
init:
	docker-compose -f docker-compose.$(CONFIG).yml run --rm -e BRANCH -e DJANGO_LOADDATA=on -e CONFIG web echo "initialization finished"

build:
	docker-compose -f docker-compose.$(CONFIG).yml build

# starts edt's docker services
start: stop
	docker-compose -f docker-compose.$(CONFIG).yml up --build -d

# starts edt's docker database service
start-db:
	docker-compose -f docker-compose.$(CONFIG).yml up db

# stops edt's docker services
stop:
	docker-compose -f docker-compose.$(CONFIG).yml stop
