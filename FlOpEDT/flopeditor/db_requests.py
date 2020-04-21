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


This module is used to declare the database interactions related to FlopEditor, an app used
to manage a department statistics for FlOpEDT.
"""


from base.models import Department, TimeGeneralSettings, Day
from people.models import Tutor, UserDepartmentSettings, SupplyStaff





def create_departments_in_database(dept_name, dept_abbrev, tutors_id):
    """Create department with admin and default settings in database

    :param dept_name: Department name
    :type dept_name: String
    :param dept_abbrev: Department abbrev
    :type dept_abbrev: String
    :param tutor_id: Tutor id
    :type tutor_id: String
    """

    dept = Department(name=dept_name, abbrev=dept_abbrev)

    dept.save()
    for tutor_id in tutors_id:
        tutor = Tutor.objects.get(id=tutor_id)
        UserDepartmentSettings(user=tutor, department=dept,
                               is_main=False, is_admin=True).save()

    TimeGeneralSettings(
        department=dept,
        day_start_time=8*60,
        day_finish_time=18*60+45,
        lunch_break_start_time=12*60+30,
        lunch_break_finish_time=14*60,
        days=[
            Day.MONDAY,
            Day.TUESDAY,
            Day.WEDNESDAY,
            Day.THURSDAY,
            Day.FRIDAY,
        ]).save()

def update_departments_in_database(old_dept_name, new_dept_name,
                                   old_dept_abbrev, new_dept_abbrev, tutors_id):
    """Update department with admin and default settings in database

    :param dept_name: Department name
    :type dept_name: String
    :param old_dept_abbrev: Old department abbrev
    :type old_dept_abbrev: String
    :param new_dept_abbrev: New department abbrev
    :type new_dept_abbrev: String
    :param tutor_id: Tutor id
    :type tutor_id: String

    """
    dept = Department.objects.get(name=old_dept_name, abbrev=old_dept_abbrev)
    # On change les noms et abbreviations du departement
    dept.name = new_dept_name
    dept.abbrev = new_dept_abbrev
    # On retire les droits a tous les Tutor
    uds = UserDepartmentSettings.objects.filter(department=dept, is_admin=True)
    for u_d in uds:
        u_d.delete()
    # On ajoute chaque nouveau responsable
    for tutor_id in tutors_id:
        tutor = Tutor.objects.get(id=tutor_id)
        UserDepartmentSettings.objects.create(user=tutor, department=dept,
                                              is_main=False, is_admin=True)
    dept.save()



def get_status_of_user(request):
    """
    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: status of user with position and employer if he's a supply_staff
    :rtype:  string status
    :rtype:  string position if supply_staff else None
    :rtype:  string employer if supply_staff else None

    """
    tutor = Tutor.objects.get(username=request.user)
    return get_status_of_tutor(tutor)

def get_status_of_tutor(tutor):
    """
    :param tutor: tutor.
    :type tutor:  people.models.Tutor
    :return: status of user with position and employer if he's a supply_staff
    :rtype:  string status
    :rtype:  string position if supply_staff else None
    :rtype:  string employer if supply_staff else None

    """
    if tutor.status == 'fs':
        status = 'Permanent'
    elif tutor.status == 'ss':
        status = 'Vacataire'
        try:
            supply_staff = SupplyStaff.objects.get(username=tutor.username)
            return status, supply_staff.position, supply_staff.employer
        except SupplyStaff.DoesNotExist:
            pass
    else:
        status = 'Biatos'
    return status, None, None