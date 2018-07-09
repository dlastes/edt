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



from base import weeks
from base.models import TrainingProgramme
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
from io import StringIO
import os
import sys
import json

@staff_member_required
def main_board(req):
    all_tps = []
    for tp in TrainingProgramme.objects.all():
        all_tps.append(tp.abbrev)
    return render(req,
                  'solve_board/main-board.html',
                  {'all_weeks': weeks.week_list(),
                   'start_date': weeks.current_week(),
                   'end_date': weeks.current_week(),
                   'current_year': weeks.annee_courante,
                   'all_train_progs': json.dumps(all_tps)})

