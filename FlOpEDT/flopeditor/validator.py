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


This module is used to declare the form validations related to FlopEditor, an app used
to manage a department statistics for FlOpEDT.
"""
import re
from base.models import Department
from people.models import Tutor


OK_RESPONSE = "OK"


def validate_department_creation(name, abbrev, tutor_id):
    """Validate parameters for department creation

    :param name: string department name
    :param abbrev: string department abbrev
    :param tutor_id: string tutor id

    :return: (boolean,json) (are the paramaters valid , status and errors)
    """
    response = {'status': 'UNKNOWN'}
    slug_re = re.compile("^[a-zA-Z]\w{1,6}$")
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
        response = {'status': OK_RESPONSE}
    return response
