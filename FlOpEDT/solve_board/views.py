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

from django.shortcuts import render

from modif import weeks

from solve_board.models import SolveRun

from django.contrib.admin.views.decorators import staff_member_required

from django.http import Http404, JsonResponse

from multiprocessing import Process
from threading import Thread

from channels import Group

from solve_board.consumers import ws_add

@staff_member_required
def main_board(req):
    return render(req,
                  'solve_board/main-board.html',
                  {'all_weeks': weeks.week_list(),
                   'start_date': weeks.current_week(),
                   'end_date': weeks.current_week(),
                   'current_year': weeks.annee_courante})


def run(req, timestamp):
    ret = {'text': u'ok'}
    if req.GET:
        start_week = int(req.GET.get('sw','0'))
        start_year = int(req.GET.get('sy','0'))
        end_week = int(req.GET.get('ew','0'))
        end_year = int(req.GET.get('ey','0'))
    else:
        ret.text = 'Sorry ?'
        return JsonResponse(ret)
    if start_week == 0 or start_year == 0 or end_week == 0 or end_year == 0:
        ret.text = "Parameters issue. 0 or not provided..."
        return JsonResponse(ret)
        
    sr = SolveRun(run_label=timestamp,
                  start_week=start_week,
                  start_year=start_year,
                  end_week=end_week,
                  end_year=end_year)
    sr.save()

    p = Comm(Group("solver"),timestamp)
    p.start()

    return JsonResponse(ret)


class Comm(Thread):
    def __init__(self, group, timestamp):
        Thread.__init__(self)
        self.group = group
        self.setName(timestamp)

    def run(self):
        self.group.send({
            "text": "Solver fired."
        })
