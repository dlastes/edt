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


This module is used to establish the crud back-end interface.
"""

from base import queries
from django.http import JsonResponse, HttpResponseForbidden

def crud_rooms(request, department_abbrev):
    """Ajax url for parameters edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    #department = get_object_or_404(Department, abbrev=department_abbrev)

    if request.method == "GET":
        allRooms = queries.get_rooms(department_abbrev)
        roomgroups = allRooms['roomgroups']
        value_set = set()
        for key in roomgroups:
            value_set.update(roomgroups[key])
        values = []
        for value in list(value_set):
            values.append((value,))
        return JsonResponse({
            "columns" :  [{
                'name': 'Nom',
                "type": "text",
                "options": {}
            }],
            "values" : values
        })
    elif request.method == "PUT":
        pass

    elif request.method == "POST":
        pass

    elif request.method == "DELETE":
        # Verifier la forme/structure de la donnée reçue par CrudJS
        # Vérifier que les salles demandées existent bien dans la base de données
        # Supprimer le(s) salle(s)
        # Retourner un message si OK ou pas
        pass

    return HttpResponseForbidden()
