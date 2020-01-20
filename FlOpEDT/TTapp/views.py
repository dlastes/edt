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

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from base.models import ScheduledCourse

from MyFlOp import MyTTUtils

            
def available_work_copies(req, dept, year, week):
    '''
    Send the content of the side panel.
    '''
    copies = list(ScheduledCourse.objects.filter(course__year=year, course__week=week, course__type__department__abbrev=dept).distinct('work_copy').values_list('work_copy'))
    copies = [n for (n,) in copies]
    copies.sort()
    return JsonResponse({'copies': copies})


def swap(req, dept, year, week, work_copy):
    '''
    Swap scheduled courses with work copy work_copy
    against scheduled courses with work copy 0
    '''
    return JsonResponse(MyTTUtils.swap_version(dept, week, year, work_copy))


def reassign_rooms(req, dept, year, week, work_copy):
    '''
    Reassign rooms of scheduled courses with work copy work_copy
    '''
    return JsonResponse(MyTTUtils.reassign_rooms(dept, week, year, work_copy))
