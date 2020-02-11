# -*- coding: utf-8 -*-
"""
Python versions: Python 3.6

This file is part of the FlOpEDT/FlOpScheduler project.
Copyright (c) 2017
Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program. If not, see
<http://www.gnu.org/licenses/>.

You can be released from the requirements of the license by purchasing
a commercial license. Buying such a license is mandatory as soon as
you develop activities involving the FlOpEDT/FlOpScheduler software
without disclosing the source code of your own applications.


This module is used to declare the views related to FlopEditor, an app used
to manage a department statistics for FlOpEDT.
"""

import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from base.models import Department, TimeGeneralSettings, Day
from base.timing import min_to_str
from base.check_admin import check_admin
from people.models import Tutor, UserDepartmentSettings
from flopeditor.check_tutor import check_tutor

@user_passes_test(check_tutor)
def home(request):
    """Main view of FlopEditor.

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: Home page rendered from the home template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    departments = Department.objects.all()
    tutors = Tutor.objects.all()
    return render(request, "flopeditor/home.html", {
        'departements': departments,
        'title': 'Choix du département',
        'admins': tutors
    })


@user_passes_test(check_tutor)
def department_default(request, department_abbrev):
    """Redirects to default department view.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the default template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    return redirect('flopeditor:flopeditor-department-parameters',
                    department_abbrev=department_abbrev)


@user_passes_test(check_tutor)
def department_parameters(request, department_abbrev):
    """Parameters view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the parameters template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    parameters = get_object_or_404(TimeGeneralSettings, department=department)
    return render(request, "flopeditor/parameters.html", {
        'title': 'Paramètres',
        'department_abbrev': department_abbrev,
        'day_start_time': min_to_str(parameters.day_start_time),
        'day_finish_time': min_to_str(parameters.day_finish_time),
        'lunch_break_start_time': min_to_str(parameters.lunch_break_start_time),
        'lunch_break_finish_time': min_to_str(parameters.lunch_break_finish_time),
        'days': parameters.days,
        'day_choices': Day.CHOICES,
        'default_preference_duration': min_to_str(parameters.default_preference_duration)

    })


def validate(name, abbrev, tutor_id):
    valid = False
    response = {'status': 'UNKNOWN'}
    slug_re = re.compile("^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
    if not name or len(name) > 50:
        response = {
            'status': 'ERROR',
            'message': "Le nom du département est invalide. \
            Il doit comporter entre 1 et 50 caractères."
        }
    elif Department.objects.filter(name=name):
        response = {
            'status': 'ERROR',
            'message': "Le nom du département est déjà utilisé. veuillez en choisir un autre."
        }
    elif not slug_re.match(abbrev):
        response = {
            'status': 'ERROR',
            'message': "L'abréviation du département est invalide. Elle peut \
            comporter des lettres et des chiffres. Elle ne doit pas comporter \
            d'espace, utilisez des '-' pour les séparations."
        }
    elif Department.objects.filter(abbrev=abbrev):
        response = {
            'status': 'ERROR',
            'message': "L'abbréviation est déjà utilisée."
        }
    elif not Tutor.objects.filter(id=tutor_id):
        response = {
            'status': 'ERROR',
            'message': "Le tuteur que vous recherchez est introuvable. \
            Veuillez en sélectionner un autre."
        }
    else:
        valid = True
        response = {'status': 'OK'}
    return valid, response

def create_departments_in_database(dept_name, abbrev, tutor_id):
    dept = Department(name=dept_name, abbrev=abbrev)
    dept.save()
    """Tutor().save()
    Room().save()
    Group().save()
    Module().save()
    CourseType().save()"""
    tutor = Tutor.objects.get(id=tutor_id)
    UserDepartmentSettings(user=tutor, department=dept, is_main=False, is_admin=True).save()
    TimeGeneralSettings(
        department=dept,
        day_start_time=8*60,
        day_finish_time=18*60+45,
        lunch_break_start_time=12*60+30,
        lunch_break_finish_time=14*60,
        days=["m", "tu", "w", "th", "f"]).save()

@user_passes_test(check_admin)
def ajax_create_department(request):
    """Ajax url for department creation

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: Server response for the creation request.
    :rtype:  django.http.JsonResponse

    """
    if request.is_ajax() and request.method == "POST":
        name = request.POST['nomDep']
        abbrev = request.POST['abbrevDep']
        tutor_id = request.POST['respDep']
        valid, response = validate(name, abbrev, tutor_id)
        if valid:
            create_departments_in_database(name, abbrev, tutor_id)
        return JsonResponse(response)
    return HttpResponseForbidden()

@user_passes_test(check_tutor)
def department_rooms(request, department_abbrev):
    """Rooms view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the rooms template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    return render(request, "flopeditor/rooms.html", {
        'title': 'Salles',
        'department_abbrev': department_abbrev
    })


@user_passes_test(check_tutor)
def department_groups(request, department_abbrev):
    """Groups view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the groups template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    return render(request, "flopeditor/groups.html", {
        'title': 'Groupes',
        'department_abbrev': department_abbrev
    })


@user_passes_test(check_tutor)
def department_modules(request, department_abbrev):
    """Modules view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the modules template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    return render(request, "flopeditor/modules.html", {
        'title': 'Modules',
        'department_abbrev': department_abbrev
    })


@user_passes_test(check_tutor)
def department_classes(request, department_abbrev):
    """Classes view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the classes template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    return render(request, "flopeditor/classes.html", {
        'title': 'Classes',
        'department_abbrev': department_abbrev
    })
