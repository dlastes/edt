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


This module is used to declare the form validations related to flop!EDITOR, an app used
to manage a department statistics for FlOpEDT.
"""
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from base.models import Department, GenericGroup
from people.models import Tutor, SupplyStaff, FullStaff, BIATOS


OK_RESPONSE = 'OK'
ERROR_RESPONSE = 'ERROR'
UNKNOWN_RESPONSE = 'UNKNOWN'


def validate_department_values(name, abbrev, tutors_id):
    """Validate parameters for department creation

    :param name: Department name
    :type name: String
    :param abbrev: department abbrev
    :type abbrev: String
    :param tutors_id: tutors' id
    :type tutors_id: List

    :return: (are the paramaters valid , status and errors)
    :rtype: (boolean,json)
    """
    response = {'status': UNKNOWN_RESPONSE}
    slug_re = re.compile(r"^[a-zA-Z]\w{0,6}$")
    if not name or len(name) > 50:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le nom du d??partement est invalide. \
            Il doit comporter entre 1 et 50 caract??res."
        }
    elif not slug_re.match(abbrev):
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'abr??viation du d??partement est invalide. Elle doit ??tre \
            entre 1 et 7 caract??res. Elle peut comporter des lettres et des chiffres \
            et doit commencer par une lettre. Elle ne doit pas comporter d'espace, \
            utilisez des '_' pour les s??parations."
        }
    else:
        for tutor_id in tutors_id:
            if not Tutor.objects.filter(id=tutor_id):
                response = {
                    'status': ERROR_RESPONSE,
                    'message': "Le tuteur que vous recherchez est introuvable. \
                    Veuillez en s??lectionner un autre."
                }
        response = {'status': OK_RESPONSE}
    return response


def validate_department_creation(name, abbrev, tutors_id):
    """Validate parameters for department creation

    :param name: Department name
    :type name: String
    :param abbrev: department abbrev
    :type abbrev: String
    :param tutors_id: tutors' id
    :type tutors_id: List

    :return: (are the paramaters valid , status and errors)
    :rtype: (boolean,json)
    """
    response = validate_department_values(name, abbrev, tutors_id)
    if response['status'] != OK_RESPONSE:
        pass
    elif Department.objects.filter(name=name):
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le nom du d??partement est d??j?? utilis??. veuillez en choisir un autre."
        }
    elif Department.objects.filter(abbrev=abbrev):
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'abbr??viation est d??j?? utilis??e."
        }
    else:
        response = {'status': OK_RESPONSE}
    return response


def validate_department_update(old_dept_name, new_dept_name,
                               old_dept_abbrev, new_dept_abbrev, tutors_id):
    """Validate parameters for department updaten

    :param old_dept_name: Old department name
    :type old_dept_name: String
    :param new_dept_name: New department name
    :type new_dept_name: String
    :param old_dept_abbrev: Old department abbreviation
    :type old_dept_abbrev: String
    :param new_dept_abbrev: New department abbreviation
    :type new_dept_abbrev: String
    :param tutors_id: tutors' id
    :type tutors_id: List

    :return: (are the paramaters valid , status and errors)
    :rtype: (boolean,json)
    """
    response = validate_department_values(
        new_dept_name, new_dept_abbrev, tutors_id)
    if response['status'] != OK_RESPONSE:
        pass
    elif old_dept_name != new_dept_name and Department.objects.filter(name=new_dept_name):
        response = {
            'status': ERROR_RESPONSE,
            'message': "Un autre d??partement poss??de d??j?? ce nom."
        }
    elif old_dept_abbrev != new_dept_abbrev and Department.objects.filter(abbrev=new_dept_abbrev):
        response = {
            'status': ERROR_RESPONSE,
            'message': "Un autre d??partement poss??de d??j?? cette abbr??viation."
        }
    else:
        response = {
            'status': OK_RESPONSE,
            'message': ''
        }
    return response


def validate_parameters_edit(days, day_start_time,
                             day_finish_time, lunch_break_start_time,
                             lunch_break_finish_time,
                             default_preference_duration):
    """Validate parameters for department creation

    :param days: List of checked working days
    :type days: List
    :param day_start_time: Day start time hh:mm
    :type day_start_time: String
    :param day_finish_time: Day finish time hh:mm
    :type day_finish_time: String
    :param lunch_break_start_time: Lunch start time hh:mm
    :type lunch_break_start_time: String
    :param lunch_break_finish_time: Lunch finish time hh:mm
    :type lunch_break_finish_time: String
    :param default_preference_duration: Class default duration hh:mm
    :type default_preference_duration: String

    :return: (boolean,json) (are the paramaters valid , status and errors)
    """
    response = {'status': UNKNOWN_RESPONSE}
    time_re = re.compile("^[0-2][0-9]:[0-5][0-9]$")
    if len(days) <= 0:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Veuillez cocher au moins un jour"
        }
    elif not time_re.match(day_start_time):
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'heure de d??but des cours est incorrecte."
        }
    elif not time_re.match(day_finish_time):
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'heure de fin des cours est incorrecte."
        }
    elif not time_re.match(lunch_break_start_time):
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'heure de d??but du d??jeuner est incorrecte."
        }
    elif not time_re.match(lunch_break_finish_time):
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'heure de fin du d??jeuner est incorrecte."
        }
    elif not time_re.match(default_preference_duration):
        response = {
            'status': ERROR_RESPONSE,
            'message': "La dur??e par d??faut d'un cours est incorrecte."
        }
    elif day_start_time > day_finish_time:
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'heure de d??but des cours doit pr??c??der l'heure de fin des cours."
        }
    elif lunch_break_start_time > lunch_break_finish_time:
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'heure de d??but du d??jeuner doit pr??c??der l'heure de fin du d??jeuner."
        }
    elif day_start_time > lunch_break_start_time or lunch_break_finish_time > day_finish_time:
        response = {
            'status': ERROR_RESPONSE,
            'message': "La p??riode du d??jeuner doit ??tre pendant la p??riode des cours."
        }
    elif default_preference_duration == "00:00":
        response = {
            'status': ERROR_RESPONSE,
            'message': "La dur??e par d??faut d'un cours ne peut pas ??tre nulle."
        }
    else:
        response = {'status': OK_RESPONSE, 'message': ''}
    return response


def validate_training_programme_values(abbrev, name, entries):
    """Validate parameters for training programme's CRUD

    :param abbrev: department abbreviation to test
    :type abbrev: str
    :param name: department name to test
    :type name: str
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: (boolean,json) (are the paramaters valid , status and errors)
    """
    # Verifie la validite du slug
    if not abbrev:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'abbreviation de la promo ne peut pas ??tre vide."])
    elif len(abbrev) > 5:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'abbreviation de la promo est trop longue."])
    # verifie la longueur du nom
    elif not name:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom de la promo ne peut pas ??tre vide."])
    elif len(name) > 50:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom de la promo est trop long."])
    else:
        return True
    return False


def validate_course_values(name, duree, entries):
    """Validate parameters for course type

    :param name: course name to test
    :type abbrev: text
    :param duree: value of duration of course
    :type abbrev: int
    :param entries: list that is returned to CrudJS
    :type abbrev: list

    :return: (boolean,json) (are the paramaters valid , status and errors)
    """
    if duree is None:
        entries['result'].append([ERROR_RESPONSE,
                                  "La dur??e est invalide"])
    elif duree < 0:
        entries['result'].append([ERROR_RESPONSE,
                                  "La dur??e ne peut pas ??tre n??gative"])
    elif not name:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom du type de cours ne peut pas ??tre vide."])
    elif len(name) > 50:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom du type de cours est trop long."])
    else:
        return True
    return False


def validate_student_structural_groups_values(entry, entries):
    """Validate parameters for student group values' CRUD

    :param abbrev: data returned by crudJS
    :type abbrev: list
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: boolean are the paramaters valid
    """
    if not entry[0]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom ne peut pas ??tre vide."])
    elif len(entry[0]) > 10:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom ne peut pas ??tre plus long que 10 caract??res."])
    elif entry[4] < 0:
        entries['result'].append([ERROR_RESPONSE,
                                  "La taille ne peut pas ??tre n??gative."])
    elif entry[0] in entry[2]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le groupe ne peut pas ??tre un sous-groupe de lui-m??me."])
    else:
        return True
    return False


def validate_student_transversal_groups_values(entry, entries):
    """Validate parameters for student group values' CRUD

    :param abbrev: data returned by crudJS
    :type abbrev: list
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: boolean are the paramaters valid
    """
    if not entry[0]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom ne peut pas ??tre vide."])
    elif len(entry[0]) > 10:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom ne peut pas ??tre plus long que 10 caract??res."])
    elif entry[5] < 0:
        entries['result'].append([ERROR_RESPONSE,
                                  "La taille ne peut pas ??tre n??gative."])
    else:
        return True
    return False


def validate_module_values(entry, entries):
    """Validate parameters for module CRUD

    :param abbrev: data returned by crudJS
    :type abbrev: list
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: boolean are the paramaters valid
    """
    if not entry[0]:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'abr??viation ne peut pas ??tre vide."])
    elif not entry[1]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le code PPN ne peut pas ??tre vide."])
    elif not entry[2]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom complet ne peut pas ??tre vide."])
    elif len(entry[0]) > 10:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'abr??viation est trop longue."])
    elif len(entry[1]) > 8:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le code PPN est trop long."])
    elif len(entry[2]) > 100:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom complet est trop long."])
    else:
        return True
    return False


def validate_period_values(name, starting_week, ending_week, entries):
    """Validate parameters for period values' CRUD

    :param name: period name to test
    :type abbrev: text
    :param starting_week: value of starting_week
    :type abbrev: int
    :param ending_week: value of ending_week
    :type abbrev: int
    :param entries: list that is returned to CrudJS
    :type abbrev: list

    :return: boolean are the paramaters valid
    """

    if starting_week is None:
        entries['result'].append([ERROR_RESPONSE,
                                  "La semaine de d??but est invalide"])
    elif ending_week is None:
        entries['result'].append([ERROR_RESPONSE,
                                  "La semaine de fin est invalide"])
    elif starting_week <= 0 or starting_week > 53:
        entries['result'].append([ERROR_RESPONSE,
                                  "La semaine de d??but doit ??tre compris entre [1-53]"])
    elif ending_week <= 0 or ending_week > 53:
        entries['result'].append([ERROR_RESPONSE,
                                  "La semaine de fin doit ??tre compris entre [1-53]"])
    elif starting_week == ending_week:
        entries['result'].append([ERROR_RESPONSE,
                                  "La semaine de d??but ne peut pas ??tre ??gale ?? la semaine de fin"])
    elif not name:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom du semestre ne peut pas ??tre vide."])
    elif len(name) > 20:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom du semestre est trop long. (<20)"])
    else:
        return True
    return False


def validate_profil_update(request):
    """
    Validate profile attributs for profile update

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: (are the paramaters valid , status and errors)
    :rtype: (boolean,json)

    """
    old_username = request.user.username
    new_username = request.POST['newIdProfil']
    new_first_name = request.POST['newFirtNameProfil']
    new_last_name = request.POST['newLastNameProfil']
    new_email = request.POST['newEmailProfil']
    new_status_vacataire = request.POST['newstatusVacataire']
    new_employer = request.POST['newEmployer']
    old_status = request.POST['oldStatus']
    tutor = Tutor.objects.get(username=old_username)


    try:
        if old_status == 'Vacataire':
            SupplyStaff.objects.get(id=tutor.id)
            tutor_exist = True
        elif old_status == 'Permanent':
            FullStaff.objects.get(id=tutor.id)
            tutor_exist = True
        else:
            BIATOS.objects.get(id=tutor.id)
            tutor_exist = True
    except Tutor.DoesNotExist:
        tutor_exist = False


    try:
        validate_email(new_email)
        email = True
    except ValidationError:
        email = False

    idregex = re.compile(r'^[\w.@+-]+$')
    if len(new_username) > 150:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le username est trop long. (<150caract??res)"
        }
    elif not idregex.match(new_username):
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le nom d'utilisateur n'est pas valide"
        }
    elif len(new_first_name) > 30:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le pr??nom est trop long. (<30caract??res)'"
        }
    elif len(new_last_name) > 150:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le nom est trop long. (<150caract??res)'"
        }
    elif not email:
        response = {
            'status': ERROR_RESPONSE,
            'message': "L'email est invalide"
        }
    elif new_status_vacataire is not None and len(new_status_vacataire) > 50:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le statut de vacataire est trop long. (<50caract??res)"
        }
    elif new_employer is not None and len(new_employer) > 50:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Le nom de l'employeur est trop long. (<50caract??res)"
        }
    elif old_username != new_username and Tutor.objects.filter(username=new_username):
        response = {
            'status': ERROR_RESPONSE,
            'message': "Id d??j?? utilis??"
        }
    elif not tutor_exist:
        response = {
            'status': ERROR_RESPONSE,
            'message': "Impossible de modifier votre profil : \
            vous n'avez pas de statut en base de donn??es"
        }
    else:
        response = {'status': OK_RESPONSE, 'message': ''}
    return response


def validate_tutor_values(entry, entries):
    """Validate parameters for tutor CRUD

    :param abbrev: data returned by crudJS
    :type abbrev: list
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: boolean are the paramaters valid
    """
    idregex = re.compile(r'^[\w.@+-]+$')
    if not entry[0]:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'id ne peut pas ??tre vide."])
    elif len(entry[0]) > 30:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'id est trop long."])
    elif not idregex.match(entry[0]):
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom d'utilisateur n'est pas valide"])
    elif not entry[1]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le pr??nom ne peut pas ??tre vide."])
    elif len(entry[1]) > 30:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le pr??nom est trop long."])
    elif not entry[2]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom ne peut pas ??tre vide."])
    elif len(entry[2]) > 30:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom est trop long."])
    elif not entry[3]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le statut ne doit pas ??tre vide."])
    elif not entry[4]:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'email' ne doit pas ??tre vide."])
    elif entry[3] != "Vacataire" and entry[5]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Seul un vacataire peut avoir une position"])
    elif entry[3] != "Vacataire" and entry[6]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Seul un vacataire peut avoir un employeur"])
    elif len(entry[5]) > 50:
        entries['result'].append([ERROR_RESPONSE,
                                  "La position est trop longue."])
    elif len(entry[6]) > 50:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'employeur est trop long."])
    else:
        return True
    return False


def validate_student_values(entry, entries):
    """Validate parameters for tutor CRUD

    :param abbrev: data returned by crudJS
    :type abbrev: list
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: boolean are the paramaters valid
    """
    idregex = re.compile(r'^[\w.@+-]+$')
    if not entry[0]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le login ne peut pas ??tre vide."])
    elif len(entry[0]) > 30:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le login est trop long."])
    elif not idregex.match(entry[0]):
        entries['result'].append([ERROR_RESPONSE,
                                  "Le login n'est pas valide"])
    elif not entry[1]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le pr??nom ne peut pas ??tre vide."])
    elif len(entry[1]) > 30:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le pr??nom est trop long."])
    elif not entry[2]:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom ne peut pas ??tre vide."])
    elif len(entry[2]) > 30:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom est trop long."])
    elif not entry[2]:
        entries['result'].append([ERROR_RESPONSE,
                                  "L'email' ne doit pas ??tre vide."])
    else:
        return True
    return False


def student_groups_from_full_names(full_names, department):
    gp_to_return = set()
    for gp_full_name in full_names:
        if gp_full_name.count('-') >= 2:
            pass

        tp, gp = gp_full_name.split('-')
        gg = GenericGroup.objects.get(train_prog__abbrev=tp, name=gp, train_prog__department=department)
        gp_to_return.add(gg)
    return gp_to_return


def validate_room_attributes_values(name, description, entries):
    """Validate parameters for room attribute's CRUD

    :param abbrev: department abbreviation to test
    :type abbrev: str
    :param name: department name to test
    :type name: str
    :param entries: list that is returned to CrudJS
    :type abbrev: list
    :return: (boolean,json) (are the paramaters valid , status and errors)
    """
    # Verifie la validite du slug
    if not name:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom de l'attribut ne peut pas ??tre vide."])
    elif len(name) > 20:
        entries['result'].append([ERROR_RESPONSE,
                                  "Le nom de l'attribut est trop long."])
    else:
        return True
    return False