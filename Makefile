#!/usr/bin/make -f
-include global.env

CONFIG ?= development
PORT ?= 8000

current_project_dir := $(shell basename ${CURDIR} | head -c 3)
default_hosts := 127.0.0.1,localhost
secret_seed = abcdefghijklmnopqrstuvwxyz0123456789!@\#$$%^&*(-_=+)

# get the current git branch name
HOSTS := $(shell [ ! -z "$(HOST)" ] && echo $(default_hosts),$(HOST) || echo $(default_hosts))
SECRET_KEY := $(shell python -c 'import random; result = "".join([random.choice("$(secret_seed)") for i in range(50)]); print(result)')
BRANCH := $(shell git branch 2>/dev/null | grep '^*' | colrm 1 2)
COMPOSE_PROJECT_NAME := edt_$(current_project_dir | tr '[:upper:]' '[:lower:]')_$(shell echo $(CONFIG) | head -c 1)_$(PORT)
export

.PHONY: config install init build start stop start-db stop-db push deploy rm debug

#
#	Create config files
#
config:
	printf "PORT=${PORT}\n" > global.env
	printf "HOST=${HOST}\n" >> global.env
	printf "CONFIG=${CONFIG}" >> global.env

install:
 	ifeq ($(CONFIG), production)
		envsubst < docker/env/web.prod.in  > docker/env/web.prod.env
		printf "POSTGRES_PASSWORD=$(shell dd if=/dev/urandom bs=1 count=32 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)" > docker/env/db.prod.env
  endif

# Initialize database with basic datas contained 
# in dump.json for tests purposes
init:
	docker-compose -f docker-compose.$(CONFIG).yml \
		run --rm \
		-e BRANCH \
		-e DJANGO_LOADDATA=on \
		-e START_SERVER=off \
		web

build:
	docker-compose -f docker-compose.$(CONFIG).yml build

# starts edt's docker services
start: stop
	docker-compose -f docker-compose.$(CONFIG).yml up --build -d

# starts edt's docker services in terminal
start_verbose: stop
	docker-compose -f docker-compose.$(CONFIG).yml up --build

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
	docker stack rm $(COMPOSE_PROJECT_NAME)	


#	Show config infos
debug:
	@echo PORT: $(PORT)
	@echo HOST: $(HOST)
	@echo HOSTS: $(HOSTS)
	@echo CONFIG: $(CONFIG)
	@echo COMPOSE_PROJECT_NAME: $(COMPOSE_PROJECT_NAME)
