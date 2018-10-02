#!/usr/bin/make -f

# get the current git branch name
BRANCH := $(shell git branch 2>/dev/null | grep '^*' | colrm 1 2)
CONFIG ?= production

export CONFIG
export BRANCH

# initialize database with basics datas #docker-compose build && 
init:
	docker-compose -f docker-compose.$(CONFIG).yml run --rm -e BRANCH -e DJANGO_LOADDATA=on -e CONFIG web

build:
	docker-compose -f docker-compose.$(CONFIG).yml build

# starts edt's docker services
start:
	docker-compose -f docker-compose.$(CONFIG).yml up --build -d

# stops edt's docker services
stop:
	docker-compose stop

test:
	echo $(CONFIG)------------
