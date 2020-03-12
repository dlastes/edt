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

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from base.models import Department, TimeGeneralSettings, Day
from FlOpEDT.decorators import dept_admin_required
from base.timing import min_to_str, str_to_min
from base.check_admin import check_admin
from people.models import Tutor
from flopeditor.check_tutor import check_tutor
from flopeditor.db_requests import create_departments_in_database
from flopeditor.validator import validate_department_creation, validate_parameters_edit, OK_RESPONSE


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
    departments = Department.objects.exclude(abbrev=department_abbrev)
    parameters = get_object_or_404(TimeGeneralSettings, department=department)
    return render(request, "flopeditor/parameters.html", {
        'title': 'Paramètres',
        'department': department,
        'day_start_time': min_to_str(parameters.day_start_time),
        'day_finish_time': min_to_str(parameters.day_finish_time),
        'lunch_break_start_time': min_to_str(parameters.lunch_break_start_time),
        'lunch_break_finish_time': min_to_str(parameters.lunch_break_finish_time),
        'days': parameters.days,
        'day_choices': Day.CHOICES,
        'default_preference_duration': min_to_str(parameters.default_preference_duration),
        'list_departments': departments,
        'has_department_perm': request.user.has_department_perm(department=department, admin=True),
        'edit': False

    })

@user_passes_test(check_tutor)
def department_parameters_edit(request, department_abbrev):
    """Parameters edit view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the parameters template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    parameters = get_object_or_404(TimeGeneralSettings, department=department)
    return render(request, "flopeditor/parameters.html", {
        'title': 'Paramètres',
        'department': department,
        'list_departments': departments,
        'day_start_time': min_to_str(parameters.day_start_time),
        'day_finish_time': min_to_str(parameters.day_finish_time),
        'lunch_break_start_time': min_to_str(parameters.lunch_break_start_time),
        'lunch_break_finish_time': min_to_str(parameters.lunch_break_finish_time),
        'days': parameters.days,
        'day_choices': Day.CHOICES,
        'default_preference_duration': min_to_str(parameters.default_preference_duration),
        'has_department_perm': request.user.has_department_perm(department=department, admin=True),
        'edit': True
    })

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
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    return render(request, "flopeditor/rooms.html", {
        'title': 'Salles',
        'department': department,
        'list_departments': departments
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
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    return render(request, "flopeditor/groups.html", {
        'title': 'Groupes',
        'department': department,
        'list_departments': departments,
        'has_dept_perm': request.user.has_department_perm(department=department, admin=True),
    })

@user_passes_test(check_tutor)
def department_training_programmes(request, department_abbrev):
    """Groups view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the groups template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    return render(request, "flopeditor/training_programmes.html", {
        'title': 'Groupes',
        'department': department,
        'list_departments': departments,
        'has_dept_perm': request.user.has_department_perm(department=department, admin=True),
    })

@user_passes_test(check_tutor)
def department_student_group_types(request, department_abbrev):
    """Groups view of FlopEditor.

    :param request:           Client request.
    :param department_abbrev: Department abbreviation.
    :type request:            django.http.HttpRequest
    :type department_abbrev:  str
    :return: Parameters page rendered from the groups template of FlopEditor.
    :rtype:  django.http.HttpResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    return render(request, "flopeditor/student_group_types.html", {
        'title': 'Groupes',
        'department': department,
        'list_departments': departments,
        'has_dept_perm': request.user.has_department_perm(department=department, admin=True),
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
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    return render(request, "flopeditor/modules.html", {
        'title': 'Modules',
        'department': department,
        'list_departments': departments
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
    department = get_object_or_404(Department, abbrev=department_abbrev)
    departments = Department.objects.exclude(abbrev=department_abbrev)
    return render(request, "flopeditor/classes.html", {
        'title': 'Classes',
        'department': department,
        'list_departments': departments
    })


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
        response = validate_department_creation(name, abbrev, tutor_id)
        if response['status'] == OK_RESPONSE:
            create_departments_in_database(name, abbrev, tutor_id)
        return JsonResponse(response)
    return HttpResponseForbidden()

@dept_admin_required
def ajax_edit_parameters(request, department_abbrev):
    """Ajax url for parameters edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    if not request.user.has_department_perm(department=department, admin=True):
        return HttpResponseForbidden()
    if request.is_ajax() and request.method == "POST":
        days = request.POST.getlist('days')
        day_start_time = request.POST['day_start_time']
        day_finish_time = request.POST['day_finish_time']
        lunch_break_start_time = request.POST['lunch_break_start_time']
        lunch_break_finish_time = request.POST['lunch_break_finish_time']
        default_preference_duration = request.POST['default_preference_duration']
        response = validate_parameters_edit(
            days,
            day_start_time,
            day_finish_time,
            lunch_break_start_time,
            lunch_break_finish_time,
            default_preference_duration)
        if response['status'] == OK_RESPONSE:
            parameters = get_object_or_404(TimeGeneralSettings, department=department)
            parameters.days = days
            parameters.day_start_time = str_to_min(day_start_time)
            parameters.day_finish_time = str_to_min(day_finish_time)
            parameters.lunch_break_start_time = str_to_min(lunch_break_start_time)
            parameters.lunch_break_finish_time = str_to_min(lunch_break_finish_time)
            parameters.default_preference_duration = str_to_min(default_preference_duration)
            parameters.save()
            response['message'] = "Les modifications ont bien été enregistrées."
        return JsonResponse(response)
    return HttpResponseForbidden()
