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

"""

from django.http import JsonResponse
from base.models import Room, RoomType, Department
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE


def read(department):
    """Return all rooms for a department

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    # Chips options
    rooms_available = list(Room.objects.values_list('name', flat=True))
    rooms_types_available = list(RoomType.objects.values_list('name', flat=True))
    departments = list(Department.objects.values_list('name', flat=True))

    # Rows
    rooms = Room.objects.filter(departments=department)
    values = []
    for room in rooms:
        values.append((room.name, [], [], []))

    return JsonResponse({
        "columns" :  [{
            'name': 'Nom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Sous-salle de...',
            "type": "select-chips",
            "options": {'values': rooms_available}
        }, {
            'name': 'Types de salles associés',
            "type": "select-chips",
            "options": {'values': rooms_types_available}
        }, {
            'name': 'Départements associés',
            "type": "select-chips",
            "options": {'values': departments}
        }],
        "values" : values
        })

def create(entries, department):
    """Create values for rooms
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['new_values'])):
        new_name = entries['new_values'][i][0]
        # verifier la longueur du nom
        if len(new_name) > 20:
            entries['result'].append([ERROR_RESPONSE,
                                      "Le nom de la salle est trop long."])
        else:

            if Room.objects.filter(name=new_name, departments=department):
                entries['result'].append([
                    ERROR_RESPONSE,
                    "La salle à ajouter est déjà présente dans la base de données."
                ])
            else:
                room = Room.objects.create(name=new_name)
                room.departments.add(department)
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

    if len(entries['old_values']) != len(entries['new_values']):
        # old and new values must have same size
        return entries
    entries['result'] = []
    for i in range(len(entries['old_values'])):
        old_name = entries['old_values'][i][0]
        new_name = entries['new_values'][i][0]
        if len(new_name) > 20:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Le nom de la salle est trop long."])
        else:
            try:
                room_to_update = Room.objects.get(name=old_name, departments=department)
                room_to_update.name = new_name
                room_to_update.save()
                entries['result'].append([OK_RESPONSE])
            except Room.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Une salle à modifier n'a pas été trouvée dans la base de données."])
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
        old_name = entries['old_values'][i][0]
        try:
            Room.objects.get(name=old_name, departments=department).delete()
            entries['result'].append([OK_RESPONSE])
        except Room.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Une salle à supprimer n'a pas été trouvée dans la base de données."])
    return entries
