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

# Week numbers issues helper
# ---------------------------

import datetime

import base.models
actual_year = 2019

days_infos = {
    'm' :{'shift': 0, 'fr_slug': 'Lun.'},
    'tu':{'shift': 1, 'fr_slug': 'Mar.'},
    'w' :{'shift': 2, 'fr_slug': 'Mer.'},
    'th':{'shift': 3, 'fr_slug': 'Jeu.'},
    'f' :{'shift': 4, 'fr_slug': 'Ven.'},
    'sa':{'shift': 5, 'fr_slug': 'Sam.'},
    'su':{'shift': 6, 'fr_slug': 'Dim.'}
}


# monday of Week #2
def monday_w2(y):
    eve = datetime.date(y, 1, 1)
    eve_w = eve.weekday()
    if eve_w < 4:
        m = eve + datetime.timedelta(7 - eve_w)
    else:
        m = eve + datetime.timedelta(14 - eve_w)
    return m


# week comprising the next working day
def current_week():
    now = datetime.date.today()
    mond = monday_w2(now.year)
    if now.weekday() > 4:
        now = now + datetime.timedelta(2)
    delta = now - mond
    return {'week': 2 + (delta.days // 7), 'year': now.year}


# list of days
def num_all_days(y, w, dept):
    if w == 0:
        return []
    monday = monday_w2(y) + datetime.timedelta(7 * (w - 2))
    day_list = []
    dept_day_list = base.models.TimeGeneralSettings.objects.get(department=dept).days
    iday = 0
    for d_ref in dept_day_list:
        cur_day = monday + datetime.timedelta(days_infos[d_ref]['shift'])
        day_list.append({'num':iday,
                         'date':f"{cur_day.day:02d}/{cur_day.month:02d}",
                         'ref':d_ref,
                         'name':days_infos[d_ref]['fr_slug']})
        iday += 1
    return day_list

# More or less working weeks
def week_list():
    li = []
    if actual_year == 2017:
        for i in list(range(36, 44)) + list(range(45, 52)):
            li.append({'week': i, 'year': 2017})
        for i in list(range(2, 9)) + list(range(10, 16)) + list(range(18, 31)):
            li.append({'week': i, 'year': 2018})
        return li
    elif actual_year == 2018:
        for i in list(range(36, 44)) + list(range(45, 52)):
            li.append({'week': i, 'year': 2018})
        for i in list(range(2, 10)) + list(range(11, 17)) + list(range(19, 31)):
            li.append({'week': i, 'year': 2019})
        return li
    else:
        # should start 1 week before the first week
        for i in list(range(35, 44)) + list(range(45, 52)):
            li.append({'week': i, 'year': actual_year})
        for i in list(range(2, 10)) + list(range(11, 17)) + list(range(19, 31)):
            li.append({'week': i, 'year': actual_year+1})
        return li


def current_year():
    now = datetime.date.today()
    if now.month < 7:
        return now.year - 1
    return now.year


def year_by_week(week):
    if week > 36:
        return current_year()
    else:
        return current_year() + 1
