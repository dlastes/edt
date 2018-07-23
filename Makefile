#!/usr/bin/make -f

# get the current git branch name
BRANCH := $(shell git branch 2>/dev/null | grep '^*' | colrm 1 2)
CONFIG ?= development
export BRANCH

# initialize database with basics datas #docker-compose build && 
init:
	docker-compose build && docker-compose run --rm -e BRANCH -e CONFIG web ./FlOpEDT/misc/init.sh

build:
	docker-compose build

# starts edt's docker services
start:
	docker-compose up -d

# stops edt's docker services
stop:
	docker-compose stop

