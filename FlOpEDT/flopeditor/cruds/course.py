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
from flopeditor.validator import validate_training_programme_values, OK_RESPONSE, ERROR_RESPONSE

def read(department):
    """Return all rooms for a department
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    possible_start_time = ["8h", "8h15", "8h30"]
    groups_types = GroupType.objects.filter(department=department)
    groups_types_name = []
    for group_type in groups_types:
        groups_types_name.append((group_type.name,))


    courses = CourseType.objects.filter(department=department)

    values = []
    for course in courses:
        values.append((course.name,course.name))
    return JsonResponse({
        "columns" :  [{
            'name': 'Liste des types de cours',
            "type": "text",
            "options": {}
        }, {
            'name': 'Liste des types de groupes concernés',
            "type": "text",
            "options": {}
        }],
        "values" : values
        })


#  {
#     'name': 'Durée (en min)',
#     "type": "text",
#     "options": {}
# }, {
#     'name': 'Horaire auquels ce type de cours peut commencer',
#     "type": "chips",
#     "options": {possible_start_time}
# }
