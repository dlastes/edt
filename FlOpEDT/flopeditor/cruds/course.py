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

"""

from django.http import JsonResponse
from base.models import CourseType, CourseStartTimeConstraint, GroupType
from flopeditor.validator import validate_course_values, OK_RESPONSE, ERROR_RESPONSE



HORAIRE_DEB = 480
HORAIRE_FIN = 1140


def possible_start_time():
    """
    Return all possibles start time
    :param department: Department.
    :type department:  base.models.Department
    :return: list of minutes
    :rtype:  list(int)

    """
    horaire = HORAIRE_DEB
    possible_start_time_list = []
    while horaire <= HORAIRE_FIN:
        minute = horaire % 60
        if minute != 0:
            possible_start_time_list.append(str(horaire // 60)+'h'+ str(minute))
        else:
            possible_start_time_list.append(str(horaire // 60)+'h')
        horaire += 15
    return possible_start_time_list


def groups_types(department):
    """
    Return all name of group type for department
    :return: list of  name of group type
    :rtype:  list(strng)

    """
    group_types = GroupType.objects.filter(department=department)
    groups_types_list = []
    for group in group_types:
        groups_types_list.append(group.name)
    return groups_types_list

def get_start_time(new_starts_times):
    """
    Return all start time in minute
    :param department: list of string (ex:"8h30").
    :type department:  list of string
    :return: list of start time in minute
    :rtype:  list(int)

    """
    start_time_list = []
    for start_time in new_starts_times:
        time = start_time.split('h')
        hours = int(time[0])
        if time[1] != "":
            minutes = int(time[1])
        else:
            minutes = 0
        start_time = 60*hours + minutes
        start_time_list.append(start_time)
    return start_time_list


def read(department):
    """Return all rooms for a department
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """


    courses = CourseType.objects.filter(department=department)

    values = []
    for course in courses:
        course_list_group = []
        for one_course_group_type in course.group_types.all():
            course_list_group.append(one_course_group_type.name)
        starts_times = CourseStartTimeConstraint.objects.filter(course_type=course)
        list_starts_times = []

        for start_time in starts_times.all():
            for value_in_minute in start_time.allowed_start_times:
                minute = value_in_minute % 60
                if minute != 0:
                    list_starts_times.append(str(value_in_minute//60)+'h'+ str(minute))
                else:
                    list_starts_times.append(str(value_in_minute//60)+'h')
        values.append((course.name, course.duration, course_list_group, list_starts_times))
    return JsonResponse({
        "columns" :  [{
            'name': 'Liste des types de cours',
            "type": "text",
            "options": {}
        }, {
            'name': 'Durée (en min)',
            "type": "text",
            "options": {}
        }, {
            'name': 'Liste des types de groupes concernés',
            "type": "select-chips",
            "options": {"values":groups_types(department)}
        }, {
            'name': 'Horaire auquels ce type de cours peut commencer',
            "type": "select-chips",
            "options": {"values":possible_start_time()}
        }],
        "values" : values
        })



def create(entries, department):
    """Create values for training programmes
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['new_values'])):
        new_course_type = entries['new_values'][i][0]
        new_duration = entries['new_values'][i][1]
        new_types_groups = entries['new_values'][i][2]
        new_starts_times = entries['new_values'][i][3]


        if not validate_course_values(new_course_type, new_duration, entries):
            pass
        elif CourseType.objects.filter(name=new_course_type, department=department):
            entries['result'].append([
                ERROR_RESPONSE,
                "Le type de cours est déjà présente dans la base de données."
            ])
        else:
            new_course = CourseType.objects.create(name=new_course_type,
                                                   department=department,
                                                   duration=new_duration)
            for name in new_types_groups:
                new_course.group_types.add(GroupType.objects.get(name=name, department=department))
            CourseStartTimeConstraint.objects.create(course_type=new_course,
                                                     allowed_start_times=get_start_time(new_starts_times))

            entries['result'].append([OK_RESPONSE])

    return entries



def update(entries, department):
    """Update values for rooms
    :param entries: Values to modify.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    if len(entries['old_values']) != len(entries['new_values']):
        # old and new values must have same size
        return entries
    for i in range(len(entries['old_values'])):
        old_course_type = entries['old_values'][i][0]
        new_course_type = entries['new_values'][i][0]
        new_duration = entries['new_values'][i][1]
        new_types_groups = entries['new_values'][i][2]
        new_starts_times = entries['new_values'][i][3]

        if validate_course_values(new_course_type, new_duration, entries):
            try:
                course_type_to_update = CourseType.objects.get(name=old_course_type,
                                                               department=department)
                course_start_time = CourseStartTimeConstraint.objects.get(course_type=course_type_to_update)
                if CourseType.objects.filter(name=new_course_type, department=department)\
                 and old_course_type != new_course_type:
                    entries['result'].append(
                        [ERROR_RESPONSE,
                         "Le nom de ce type de cours est déjà utilisée."])
                else:
                    course_type_to_update.name = new_course_type
                    course_type_to_update.duration = new_duration

                    course_type_to_update.group_types.through.objects.all().delete()
                    for name in new_types_groups:
                        course_type_to_update.group_types.add(GroupType.objects.get(name=name,
                                                                                    department=department))

                    course_start_time.allowed_start_times = get_start_time(new_starts_times)

                    course_start_time.save()
                    course_type_to_update.save()
                    entries['result'].append([OK_RESPONSE])
            except CourseType.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Un type de cours à modifier n'a pas été trouvée dans la base de données."])
            except CourseType.MultipleObjectsReturned:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Plusieurs type de cours du même nom existent en base de données."])

    return entries

def delete(entries, department):
    """Delete values for rooms
    :param entries: Values to delete.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        old_course_type = entries['old_values'][i][0]
        old_duration = entries['old_values'][i][1]

        try:
            CourseType.objects.get(name=old_course_type,
                                   department=department,
                                   duration=old_duration).delete()
            entries['result'].append([OK_RESPONSE])
        except CourseType.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Une promo à supprimer n'a pas été trouvée dans la base de données."])
    return entries
