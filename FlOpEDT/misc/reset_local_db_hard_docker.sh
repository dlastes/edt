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

echo "ATTENTION -- WARNING -- ACHTUNG"
echo "Tout ce qui se trouve sur cette base de donnée sera perdu"
echo "Continuer ? (oui ?)"
read rep
if [ $rep = "oui" ]
then
    BASE='..'
    sudo systemctl restart postgresql
    sudo -u postgres psql -c 'drop database "FlOp_database_abst-gen"'
    sudo -u postgres createdb "FlOp_database_abst-gen"
    apps="modif TTapp quote people"
    for a in $apps
    do
	mig=$a/migrations
	for i in `ls $BASE/$mig --hide=__init__.py`
	do
	    rm $BASE/$mig/$i
	done
    done
    # mig='TTapp/migrations'
    # for i in `ls $BASE/$mig --hide=__init__.py`
    # do
    # 	rm $BASE/$mig/$i
    # done
    # mig='quote/migrations'
    # for i in `ls $BASE/$mig --hide=__init__.py`
    # do
    # 	rm $BASE/$mig/$i
    # done
    m=$BASE/"manage.py"
    s="FlOpEDT.settings.development"
    python $m makemigrations --settings=$s
    python $m migrate --settings=$s
fi
