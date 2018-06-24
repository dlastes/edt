# -*- coding: utf-8 -*-

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

from __future__ import unicode_literals

from modif import weeks
from people.models import FullStaff
from solve_board.models import SolveRun
from solve_board.consumers import ws_add
from MyFlOp.MyTTModel import MyTTModel

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, JsonResponse
from django.conf import settings

from channels import Group

from multiprocessing import Process
from threading import Thread
from StringIO import StringIO
import os
import sys

@staff_member_required
def main_board(req):
    return render(req,
                  'solve_board/main-board.html',
                  {'all_weeks': weeks.week_list(),
                   'start_date': weeks.current_week(),
                   'end_date': weeks.current_week(),
                   'current_year': weeks.annee_courante})


# def pripri(s):
#     print s
#     Group("solver").send({'text':'qwe'})
#     Group("solver").send({'text':s})
#     for p in FullStaff.objects.all():
#         print p

# def run(req, timestamp):
#     ret = {'text': u'ok'}
#     if req.GET:
#         start_week = int(req.GET.get('sw','0'))
#         start_year = int(req.GET.get('sy','0'))
#         end_week = int(req.GET.get('ew','0'))
#         end_year = int(req.GET.get('ey','0'))
#     else:
#         ret.text = u'Sorry ?'
#         return JsonResponse(ret)
#     if start_week == 0 or start_year == 0 or end_week == 0 or end_year == 0:
#         ret.text = u"Parameters issue. 0 or not provided..."
#         return JsonResponse(ret)

#     if end_year < start_year \
#        or end_year == start_year and end_week < start_week:
#         ret.text = u"End before start?"
#         return JsonResponse(ret)

#     for year in range(start_year, end_year + 1):
#         for week in range(1,54):
#             if (week >= start_week and year == start_year \
#                 or year > start_year) \
#                 and (week <= end_week and year == end_year \
#                      or year < end_year):
#                 sr = SolveRun(run_label=timestamp,
#                               start_week=week,
#                               start_year=year,
#                               end_week=week,
#                               end_year=year)
#                 sr.save()
# #                p = Process(target=pripri, args=('wewr',))
# #                p = SpawnSolve(Group("solver"), timestamp, week, year)
# #                p.start()

#     return JsonResponse(ret)



# class SpawnSolve(Thread):
#     def __init__(self, group, timestamp, week, year):
#         Thread.__init__(self)
#         self.group = group
#         self.setName(timestamp)
#         self.week = week
#         self.year = year
#         self.group.send({'text':
#                          'Year: ' + str(year) + ' ; week: ' + str(week) })

#     def run(self):
#         out = Tee(str(self.year)+ '-' + str(self.week) + '--'
#                   + self.getName() + '.log', self.group)
#         sys.stdout = out

#         try:
#             t = MyTTModel(self.week, self.year)
#             t.solve()
#         finally:
#             out.close()
#             sys.stdout = sys.__stdout__


