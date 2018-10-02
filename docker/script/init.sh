#!/bin/bash

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

echo "Wait until Postgres is definitely ready to start migrations"
$SCRIPT_PATH/wait-for-it.sh db:5432 -- echo "Postgres is up - continuing"

if [ "x$DJANGO_COLLECTSTATIC" = 'xon' ]; then
    /code/FlOpEDT/manage.py collectstatic --noinput
fi

if [ "x$DJANGO_MIGRATE" = 'xon' ]; then
    echo "manage.py migrate..."
    /code/FlOpEDT/manage.py makemigrations
    /code/FlOpEDT/manage.py migrate --noinput
fi

if [ "x$DJANGO_LOADDATA" = 'xon' ]; then
  echo "manage.py loaddata..."
  /code/FlOpEDT/manage.py loaddata dump.json
fi

exec "$@"