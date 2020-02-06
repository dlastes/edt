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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from base.models import Department, TimeGeneralSettings
from people.models import Tutor
from flopeditor.check_tutor import check_tutor
from django.shortcuts import get_object_or_404



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
    :return: Parameters page rendered from the parameters template of FlopEditor.
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
        'title': 'Parametres',
        'department_abbrev': department_abbrev,
        'day_start_time': parameters.day_start_time,
        'day_finish_time': parameters.day_finish_time ,
        'lunch_break_start_time':parameters.lunch_break_start_time ,
        'lunch_break_finish_time': parameters.lunch_break_finish_time ,
        'days': parameters.days

    })


@user_passes_test(check_tutor)
def department_rooms(request, department_abbrev):
    """Rooms view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the parameters template of FlopEditor.
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
    :return: Parameters page rendered from the parameters template of FlopEditor.
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
    :return: Parameters page rendered from the parameters template of FlopEditor.
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
    :return: Parameters page rendered from the parameters template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    return render(request, "flopeditor/classes.html", {
        'title': 'Classes',
        'department_abbrev': department_abbrev
    })
