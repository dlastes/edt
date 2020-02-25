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
    slug_re = re.compile("^[a-zA-Z]\w{0,6}$")
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
            'message': "L'abréviation du département est invalide. Elle doit être entre 1 et 7 caractères. \
		Elle peut comporter des lettres et des chiffres et doit commencer par une lettre. Elle ne \
		doit pas comporter d'espace, utilisez des '_' pour les séparations."
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


def validate_parameters_edit(days, day_start_time, day_finish_time, lunch_break_start_time, lunch_break_finish_time, default_preference_duration):
    """Validate parameters for department creation

    :param days: array List of checked working days
    :param day_start_time: string day start time hh:mm
    :param day_finish_time: string day finish time hh:mm
    :param lunch_break_start_time: string lunch start time hh:mm
    :param lunch_break_finish_time: string lunch finish time hh:mm
    :param default_preference_duration: string class default duration hh:mm

    :return: (boolean,json) (are the paramaters valid , status and errors)
    """
    response = {'status': 'UNKNOWN'}
    time_re = re.compile("^[0-2][0-9]:[0-5][0-9]$")
    if len(days) <= 0:
        response = {
            'status': 'ERROR',
            'message': "Veuillez cocher au moins un jour"
        }
    elif not time_re.match(day_start_time):
        response = {
            'status': 'ERROR',
            'message': "L'heure de début des cours est incorrecte."
        }
    elif not time_re.match(day_finish_time):
        response = {
            'status': 'ERROR',
            'message': "L'heure de fin des cours est incorrecte."
        }
    elif not time_re.match(lunch_break_start_time):
        response = {
            'status': 'ERROR',
            'message': "L'heure de début du déjeuner est incorrecte."
        }
    elif not time_re.match(lunch_break_finish_time):
        response = {
            'status': 'ERROR',
            'message': "L'heure de fin du déjeuner est incorrecte."
        }
    elif not time_re.match(default_preference_duration):
        response = {
            'status': 'ERROR',
            'message': "La durée par défaut d'un cours est incorrecte."
        }
    elif day_start_time > day_finish_time:
        response = {
            'status': 'ERROR',
            'message': "L'heure de début des cours doit précéder l'heure de fin des cours."
        }
    elif lunch_break_start_time > lunch_break_finish_time:
        response = {
            'status': 'ERROR',
            'message': "L'heure de début du déjeuner doit précéder l'heure de fin du déjeuner."
        }
    elif day_start_time > lunch_break_start_time or lunch_break_finish_time > day_finish_time:
        response = {
            'status': 'ERROR',
            'message': "La période du déjeuner doit être pendant la période des cours."
        }
    elif default_preference_duration == "00:00":
        response = {
            'status': 'ERROR',
            'message': "La durée par défaut d'un cours ne peut pas être nulle."
        }
    else:
        response = {'status': OK_RESPONSE, 'message':''}
    return response
