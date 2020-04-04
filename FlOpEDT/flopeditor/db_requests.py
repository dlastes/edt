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
from people.models import Tutor, UserDepartmentSettings


def create_departments_in_database(dept_name, dept_abbrev, tutors_id):
    """Create department with admin and default settings in database

    :param dept_name: string department name
    :param dept_abbrev: string department abbrev
    :param tutor_id: string tutor id

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
