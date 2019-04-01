#!/usr/bin/make -f

# get the current git branch name
export BRANCH := $(shell git branch 2>/dev/null | grep '^*' | colrm 1 2)

export CONFIG ?= development
CURRENT_PROJECT_DIR := $(shell basename ${CURDIR} | head -c 3)
export LOCALHOST_PORT ?= 8000
export COMPOSE_PROJECT_NAME := edt_$(CURRENT_PROJECT_DIR)_$(shell echo $(CONFIG) | head -c 1)_$(LOCALHOST_PORT)

build:
	docker-compose -f docker-compose.$(CONFIG).yml build

# initialize database with basic datas contained 
# in dump.json for tests purposes
init:
	docker-compose -f docker-compose.$(CONFIG).yml \
		run --rm \
		-e BRANCH \
		-e DJANGO_LOADDATA=on \
		-e START_SERVER=off \
		web

# starts edt's docker services
start: stop
	docker-compose -f docker-compose.$(CONFIG).yml up --build -d

# stops edt's docker services
stop:
	docker-compose -f docker-compose.$(CONFIG).yml stop

# starts edt's docker database service
start-db:
	docker-compose -f docker-compose.$(CONFIG).yml up -d db

stop-db:
	docker-compose -f docker-compose.$(CONFIG).yml stop db

#
#	Docker stack helpers
#
push: build
	docker-compose -f docker-compose.$(CONFIG).yml push

deploy:
	docker stack deploy --compose-file docker-compose.$(CONFIG).yml $(COMPOSE_PROJECT_NAME)

rm:
	docker stack rm edt_$(COMPOSE_PROJECT_NAME)	


#	Show config infos
debug:
	@echo CURRENT_PROJECT_DIR: $(CURRENT_PROJECT_DIR)
	@echo COMPOSE_PROJECT_NAME: $(COMPOSE_PROJECT_NAME)
	@echo LOCALHOST_PORT: $(LOCALHOST_PORT)