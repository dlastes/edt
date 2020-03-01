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
from base.models import Room
from FlOpEDT.decorators import dept_admin_required, tutor_required

@tutor_required
def read(request, department):
    """Return all rooms for a department

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    rooms = Room.objects.filter(departments=department)
    values = []
    for room in rooms:
        values.append((room.name,))
    return JsonResponse({
        "columns" :  [{
            'name': 'Nom',
            "type": "text",
            "options": {}
        }],
        "values" : values
    })