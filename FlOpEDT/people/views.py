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

import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from FlOpEDT.decorators import tutor_or_superuser_required

import base.queries as queries

from people.models import Tutor, GroupPreferences, StudentPreferences, Student,\
    NotificationsPreferences, UserPreferredLinks, PhysicalPresence, User
from people.admin import TutorResource, GroupPreferencesResource, \
    StudentPreferencesResource, UserPreferredLinksResource, PhysicalPresenceResource


logger = logging.getLogger(__name__)


def redirect_add_people_kind(req, kind):
    if kind == "stud":
        return redirect('people:add_student')
    elif kind == "full":
        return redirect('people:add_fullstaff')
    elif kind == "supp":
        return redirect('people:add_supplystaff')
    elif kind == "BIAT":
        return redirect('people:add_BIATOS')
    else:
        raise Http404("I don't know this kind of people.")


@login_required
def redirect_change_people_kind(req):
    if req.user.is_student:
        return redirect('people:change_student')
    if req.user.is_tutor:
        if req.user.tutor.status == Tutor.FULL_STAFF:
            return redirect('people:change_fullstaff')
        if req.user.tutor.status == Tutor.SUPP_STAFF:
            return redirect('people:change_supplystaff')
        if req.user.tutor.status == Tutor.BIATOS:
            return redirect('people:change_BIATOS')
    else:
        raise Http404("Who are you?")


def fetch_tutors(req):
    dataset = TutorResource().export(Tutor.objects.all())
    response = HttpResponse(dataset.csv,
                                content_type='text/csv')
    return response


def fetch_preferences_group(req):
    dataset = GroupPreferencesResource().export(GroupPreferences.objects.all())
    response = HttpResponse(dataset.csv,
                                content_type='text/csv')
    return response


def fetch_preferences_students(req):
    dataset = StudentPreferencesResource().export(StudentPreferences.objects.all())
    response = HttpResponse(dataset.csv,
                                content_type='text/csv')
    return response


@login_required
def student_preferences(req):
    if req.method=='POST' :
        logger.info(f'REQ: student preferences {req}')
        if req.user.is_authenticated and req.user.is_student:
            user = req.user
            morning_weight = req.POST['morning_evening']
            free_half_day_weight = req.POST['light_free']

            student = Student.objects.get(username=user.username)
            student_pref, created = StudentPreferences.objects.get_or_create(student=student)
            if created:
                student_pref.save()
            student_pref.morning_weight = morning_weight
            student_pref.free_half_day_weight = free_half_day_weight
            student_pref.save()
            group_pref = None
            for group in student.belong_to.all() :
                group_pref, created = GroupPreferences.objects.get_or_create(group=group)
                if created:
                    group_pref.save()
            if group_pref is not None:
                group_pref.calculate_fields()
                group_pref.save()
            return redirect("base:edt", department=req.department)
        else:
            raise Http404("Who are you?")
    else:
        if req.user.is_authenticated and req.user.is_student:
            student = Student.objects.get(username=req.user.username)
            try:
                student_pref = StudentPreferences.objects.get(student=student)
            except ObjectDoesNotExist:
                student_pref = StudentPreferences(student=student)
                student_pref.save()
            morning = student_pref.morning_weight
            free_half_day = student_pref.free_half_day_weight
            return TemplateResponse(
                req,
                'people/studentPreferencesSelection.html',
                {'morning': morning,
                 'free_half_day': free_half_day,
                 'user_notifications_pref':
                 queries.get_notification_preference(req.user)
                })
        else:
            # Make a decorator instead
            raise Http404("Who are you?")


def create_user(req):
    logger.info(f'REQ: create user {req.user}')
    logger.info(f'has dpt perm: {req.has_department_perm}')
    return TemplateResponse(req, 'people/login_create.html')


def fetch_user_preferred_links(req, **kwargs):
    pref = UserPreferredLinks.objects\
                         .prefetch_related('user__departments')\
                         .filter(user__departments=req.department)
    dataset = UserPreferredLinksResource().export(pref)
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response
    

def fetch_physical_presence(req, year, week, **kwargs):
    presence = PhysicalPresence.objects.filter(user__departments=req.department,
                                               year=year,
                                               week=week)
    dataset = PhysicalPresenceResource().export(presence)
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response


@tutor_or_superuser_required
def change_physical_presence(req, year, week, user):
    bad_response = {'status': 'KO'}

    if not req.is_department_admin and req.user.username != user:
        bad_response['more'] = _(f'Not allowed')
        return JsonResponse(bad_response)

    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        bad_response['more'] = _(f'No such user as {user}')
        return JsonResponse(bad_response)

    
    good_response = {'status': 'OK', 'more': ''}

    changes = json.loads(req.POST.get('changes', '{}'))
    logger.info("List of changes")
    for change in changes:
        logger.info(change)

    # Default week at None
    if week == 0 or year == 0:
        week = None
        year = None

    for change in changes:
        logger.info(f"Change {change}")
        if not change['force_here']:
            PhysicalPresence.objects.filter(week=week,
                                            year=year,
                                            day=change['day'],
                                            user=user).delete()
        else:
            PhysicalPresence.objects.create(week=week,
                                            year=year,
                                            day=change['day'],
                                            user=user)

    return JsonResponse(good_response)

