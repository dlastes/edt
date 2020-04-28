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
from people.models import Tutor, SupplyStaff, User, FullStaff, BIATOS, UserDepartmentSettings
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE, validate_tutor_values
from flopeditor.db_requests import get_status_of_tutor

def has_rights_to_delete_tutor(user, tutor, entries):
    """
    :param user: User trying to create or delete a tutor.
    :type user:  people.models.User
    :param tutor: Tutor to add/delete.
    :type tutor:  base.models.Room
    :return: True if user has rights.
    :rtype:  Boolean
    """

    if user.username == tutor.username:
        entries['result'].append(
            [ERROR_RESPONSE,
             "Vous ne pouvez pas vous supprimer vous-même."])
        return False
    if not user.is_superuser and tutor.is_superuser:
        entries['result'].append(
            [ERROR_RESPONSE,
             "Vous n'avez pas les droits nécessaires pour supprimer cet utilisateur."])
        return False
    for dept in tutor.departments.all():
        if not user.has_department_perm(department=dept, admin=True):
            entries['result'].append([
                ERROR_RESPONSE,
                "Vous ne pouvez pas supprimer un intervenant avec un département (" +
                dept.name+") dont vous n'êtes pas responsable."
            ])
            return False
    return True


def has_rights_to_create_tutor(user, tutor, entries):
    """
    :param user: User trying to create or delete a tutor.
    :type user:  people.models.User
    :param tutor: Tutor to add/delete.
    :type tutor:  base.models.Room
    :return: True if user has rights.
    :rtype:  Boolean
    """

    for dept in tutor.departments.all():
        if not user.has_department_perm(department=dept, admin=True):
            entries['result'].append([
                ERROR_RESPONSE,
                "Vous ne pouvez pas créer un intervenant avec un département (" +
                dept.name+") dont vous n'êtes pas responsable."
            ])
            return False
    return True


def has_rights_to_update_tutor(user, entries, i):
    """
    :param user: User trying to create or delete a tutor.
    :type user:  people.models.User
    :param entries: flopeditor list.
    :type room:  list
    :return: True if user has rights.
    :rtype:  Boolean

    """
    if set(entries['new_values'][i][7]) == set(entries['old_values'][i][7]):
        departments = Department.objects.filter(
            name__in=entries['new_values'][i][7])
        if not departments:
            return True
        for dept in departments:
            if user.has_department_perm(department=dept, admin=True):
                return True
        entries['result'].append([
            ERROR_RESPONSE,
            "Vous ne pouvez pas modifier un intervenant dont vous n'êtes pas responsbale."
        ])
        return False

    old_departments = Department.objects.filter(
        name__in=entries['old_values'][i][7])

    new_departments = Department.objects.filter(
        name__in=entries['new_values'][i][7])

    for dep in old_departments:
        if not user.has_department_perm(department=dep, admin=True) and dep not in new_departments:
            entries['result'].append([
                ERROR_RESPONSE,
                "Impossible de retirer d'un intervenant" +
                " un département dont vous n'êtes pas responsable."
            ])
            return False

    for dep in new_departments:
        if not user.has_department_perm(department=dep, admin=True) and dep not in old_departments:
            entries['result'].append([
                ERROR_RESPONSE,
                "Impossible d'ajouter à un intervenant" +
                " un département dont vous n'êtes pas responsable."
            ])
            return False

    return True


# pylint: disable=W0613
def read(department):
    """Return all rooms
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    tutors = Tutor.objects.all()
    values = []
    for tut in tutors:
        status, position, employer = get_status_of_tutor(tut)
        values.append((tut.username, tut.first_name, tut.last_name, status, tut.email,
                       position, employer, list(tut.departments.values_list('name', flat=True))))

    return JsonResponse({
        "columns":  [{
            'name': 'Id',
            "type": "text",
            "options": {}
        }, {
            'name': 'Prénom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Nom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Statut',
            "type": "select",
            "options": {'values': ["Permanent", "Vacataire", "Biatos"]}
        }, {
            'name': 'Email',
            "type": "text",
            "options": {}
        }, {
            'name': 'Position',
            "type": "text",
            "options": {}
        }, {
            'name': 'Employeur',
            "type": "text",
            "options": {}
        }, {
            'name': 'Départements',
            "type": 'select-chips',
            "options": {'values': list(Department.objects.values_list('name', flat=True))}
        }],
        "values": values,
        "options": {
            "deleteMessage": "Si vous supprimez cet intervenant," +
            " tous les cours associés seront supprimés et ce dernier ne pourra plus se connecter."
        }
    })


# pylint: disable=W0613
def create(request, entries, department):
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
        if not validate_tutor_values(entries['new_values'][i], entries):
            pass
        elif User.objects.filter(username=entries['new_values'][i][0]):
            entries['result'].append([
                ERROR_RESPONSE,
                "Un utilisateur avec cet id existe déjà."
            ])
        else:
            tutor = None

            if entries['new_values'][i][3] == "Vacataire":
                tutor = SupplyStaff.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    status=Tutor.SUPP_STAFF,
                    email=entries['new_values'][i][4],
                    position=entries['new_values'][i][5],
                    employer=entries['new_values'][i][6])
            elif entries['new_values'][i][3] == "Permanent":
                tutor = FullStaff.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    status=Tutor.FULL_STAFF,
                    email=entries['new_values'][i][4])
            elif entries['new_values'][i][3] == "Biatos":
                tutor = BIATOS.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    status=Tutor.BIATOS,
                    email=entries['new_values'][i][4])

            tutor.departments.set(Department.objects.filter(
                name__in=entries['new_values'][i][7]))

            if has_rights_to_create_tutor(request.user, tutor, entries):
                tutor.save()
                entries['result'].append([OK_RESPONSE])
            else:
                tutor.delete()
    return entries


# pylint: disable=W0613
def update(request, entries, department):
    """Update values for tutors
    :param entries: Values to modify.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    if len(entries['old_values']) != len(entries['new_values']):
        return entries

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        if not has_rights_to_update_tutor(request.user, entries, i):
            pass
        elif not validate_tutor_values(entries['new_values'][i], entries):
            pass
        # elif entries['new_values'][i][3] != entries['old_values'][i][3]:
        #     #NB: c'est le cas où il faudrait changer un objet de classe
        #     entries['result'].append([
        #         ERROR_RESPONSE,
        #         "Opération non supportée."
        #     ])
        elif User.objects.filter(username=entries['new_values'][i][0]) and \
                entries['old_values'][i][0] != entries['new_values'][i][0]:
            entries['result'].append([
                ERROR_RESPONSE,
                "Un utilisateur avec cet id existe déjà."
            ])
        else:
            try:
                if entries['new_values'][i][3] != entries['old_values'][i][3]:
                    tutor_to_update = Tutor.objects.get(
                        username=entries['old_values'][i][0])
                    if entries['new_values'][i][3] == "Vacataire":
                        new = SupplyStaff(tutor_ptr_id=tutor_to_update.id)
                        new.__dict__.update(tutor_to_update.__dict__)
                        new.status = Tutor.SUPP_STAFF
                        new.position = entries['new_values'][i][5]
                        new.employer = entries['new_values'][i][6]
                    elif entries['new_values'][i][3] == "Permanent":
                        new = FullStaff(tutor_ptr_id=tutor_to_update.id)
                        new.__dict__.update(tutor_to_update.__dict__)
                        new.status = Tutor.FULL_STAFF
                    else:
                        new = BIATOS(tutor_ptr_id=tutor_to_update.id)
                        new.__dict__.update(tutor_to_update.__dict__)
                        new.status = Tutor.BIATOS
                    
                    new.username = entries['new_values'][i][0]
                    new.first_name = entries['new_values'][i][1]
                    new.last_name = entries['new_values'][i][2]
                    new.email = entries['new_values'][i][4]
                    new.departments.set(Department.objects.filter(
                        name__in=entries['new_values'][i][7]))
                    new.save()

                    if entries['old_values'][i][3] == "Vacataire":
                        SupplyStaff.objects.get(id=tutor_to_update.id).delete(keep_parents=True)
                    elif entries['old_values'][i][3] == "Permanent":
                        FullStaff.objects.get(id=tutor_to_update.id).delete(keep_parents=True)
                    else:
                        BIATOS.objects.get(id=tutor_to_update.id).delete(keep_parents=True)
                    entries['result'].append([OK_RESPONSE])
                else:
                    tutor_to_update = Tutor.objects.get(
                        username=entries['old_values'][i][0])

                    if entries['new_values'][i][3] == "Vacataire":
                        tutor_to_update.status = Tutor.SUPP_STAFF
                        tutor_to_update = SupplyStaff.objects.get(
                            username=entries['old_values'][i][0])
                        tutor_to_update.position = entries['new_values'][i][5]
                        tutor_to_update.employer = entries['new_values'][i][6]
                    elif entries['new_values'][i][3] == "Permanent":
                        tutor_to_update.status = Tutor.FULL_STAFF
                    elif entries['new_values'][i][3] == "Biatos":
                        tutor_to_update.status = Tutor.BIATOS

                    tutor_to_update.username = entries['new_values'][i][0]
                    tutor_to_update.first_name = entries['new_values'][i][1]
                    tutor_to_update.last_name = entries['new_values'][i][2]
                    tutor_to_update.email = entries['new_values'][i][4]
                    tutor_to_update.departments.set(Department.objects.filter(
                        name__in=entries['new_values'][i][7]))

                    tutor_to_update.save()

                    entries['result'].append([OK_RESPONSE])
            except Tutor.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Un intervenant à modifier n'a pas été trouvée dans la base de données."])
    return entries


def delete(request, entries, department):
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
        username = entries['old_values'][i][0]
        try:
            tutor = Tutor.objects.get(username=username)

            if has_rights_to_delete_tutor(request.user, tutor, entries):
                tutor.delete()
                entries['result'].append([OK_RESPONSE])

        except Tutor.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un intervenant à supprimer n'a pas été trouvé dans la base de données."])
    return entries
