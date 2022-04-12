# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

import django
import os
from datetime import date
from FlOpEDT.decorators import timer
from base.models import Course, ScheduledCourse, Week, GenericGroup
from notifications.models import BackUpModif
from base.timing import flopdate_to_datetime, Day, french_format
from people.models import Tutor, NotificationsPreferences
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

from django.core.mail import send_mail
from django.utils.html import strip_tags


@timer
def backup():
    print("Deleting old backup")
    BackUpModif.objects.filter(new=False).delete()
    print("Old backup deleted")
    print("Converting recent backup in old one")
    old_backup = BackUpModif.objects.filter(new=True)
    for b in old_backup:
        b.new = False
        b.save()
    print("Old backup conversion done")
    print("New backup started")
    #Get week number by using isocalendar
    today = date.today()
    week_number = date(today.year, today.month, today.day).isocalendar()[1]
    week = Week.objects.get(nb=week_number, year=today.year)

    courses = Course.objects.filter(week__gte=week)
    scheduled_courses = ScheduledCourse.objects.filter(work_copy=0,
                                                       course__in=courses)

    for course in courses:
        #Get all fields necessary for modification check
        #A course can not be in ScheduledCourse
        scheduled_course=scheduled_courses.filter(course=course)
        if scheduled_course.exists():
            scheduled_course = scheduled_course[0]
            week = course.week.nb
            year = course.week.year
            day = scheduled_course.day
            module = course.module.abbrev
            #Can have no tutor
            tutor = scheduled_course.tutor.username if scheduled_course.tutor != None else None
            #Can have no supp_tutors
            supp_tutors = list(course.supp_tutor.all()) if course.supp_tutor != None else None
            start_time = scheduled_course.start_time
            #Can have no room
            room = scheduled_course.room.name if scheduled_course.room != None else None
            #Multiple groups are possible for a single course
            groups = list(course.groups.all())
            for group in groups:
                train_prog = group.train_prog.abbrev
                department = group.train_prog.department.abbrev
                #Create a new BackUpModif object which represent the table used for backup, fill it and then save it
                line = BackUpModif()
                line.new = True
                line.week = week
                line.year = year
                line.day = day
                line.module_abbrev = module
                line.tutor_username = tutor
                line.supp_tutor_usernames = supp_tutors
                line.start_time = start_time
                line.room_name = room
                line.group_name = group.name
                line.department_abbrev = department
                line.train_prog_name = train_prog
                line.save()
    print("Backup done")
    print("Number of courses saved : " + str(BackUpModif.objects.filter(new=True).count()))

@timer
def check_modifs():
    new_backup = set(BackUpModif.objects.filter(new=True))
    old_backup = set(BackUpModif.objects.filter(new=False))
    news = new_backup - old_backup
    olds = old_backup - new_backup
    changes = olds | news

    # Create two dict that will be save as JSON at the end
    dict_modif_student = {}
    dict_modif_tutor = {}

    departments = {change.department_abbrev for change in changes}

    # Initialise user dict with all departments
    for department in departments:
        dict_modif_student[department] = {}

    for change in changes:
        if change in olds:
            mode = "delete"
        else:
            mode = "create"
        group = change.group_name
        department = change.department_abbrev
        train_prog = change.train_prog_name
        tutor_username = change.tutor_username
        module = change.module_abbrev
        room = change.room_name
        start_time = change.start_time
        week = Week.objects.get(year=change.year, nb=change.week)
        day = Day(week=week, day=change.day)
        datetime = flopdate_to_datetime(day, change.start_time)

        # Store all changes for users
        if train_prog not in dict_modif_student[department]:
            dict_modif_student[department][train_prog] = {}
        if group not in dict_modif_student[department][train_prog]:
            dict_modif_student[department][train_prog][group] = []
        student_object = {gettext('Mode'): mode,
                          gettext('Date'): datetime.date(),
                          gettext('Start time'): french_format(start_time),
                          gettext('Module'): module,
                          gettext('Tutor'): tutor_username,
                          gettext('Room'): room}
        dict_modif_student[department][train_prog][group].append(student_object)

        # Store all changes for tutors
        if tutor_username not in dict_modif_tutor:
            dict_modif_tutor[tutor_username] = {}
        if department not in dict_modif_tutor[tutor_username]:
            dict_modif_tutor[tutor_username][department] = []
        tutor_object = {gettext('Mode'): mode,
                        gettext('Date'): datetime.date(),
                        gettext('Start time'): french_format(start_time),
                        gettext('Module'): module,
                        gettext('Train_prog'): train_prog,
                        gettext('Group'): group,
                        gettext('Room'): room}
        dict_modif_tutor[tutor_username][department].append(tutor_object)
    return dict_modif_student, dict_modif_tutor

@timer
def send_notifications():
    today = date.today()
    dict_modif_student, dict_modif_tutor = check_modifs()
    cpt = 0
    subject = _("[flop!Scheduler] Changes on your planning")

    for tutor_username, dic in dict_modif_tutor.items():
        if tutor_username is None:
            continue
        tutor = Tutor.objects.get(username=tutor_username)
        notif, c = NotificationsPreferences.objects.get_or_create(user=tutor)
        nb_of_notified_weeks = notif.nb_of_notified_weeks
        if not nb_of_notified_weeks:
            continue
        nb_of_notified_days = 7 * nb_of_notified_weeks
        intro_text = _("Hi ") + tutor.first_name + "<br />"
        intro_text += _("Here are the changes of your planning for the %g following days :") % nb_of_notified_days
        intro_text += "<br /> <br />"
        html_msg = ""
        for department, changes in dic.items():
            filtered_changes = [change for change in changes
                                if 0 <= (change[gettext('Date')] - today).days <= nb_of_notified_days]

            if not filtered_changes:
                continue

            filtered_changes.sort(key=lambda x: (x[gettext('Date')], x[gettext('Start time')]))
            html_msg += _("For the department %s :") % department + "<br />"
            html_msg += changes_in_html_string(filtered_changes)
        send_changes_email(subject, intro_text, html_msg, to_email=tutor.email)

    students = set()

    for dept_abbrev in dict_modif_student:
        for train_prog in dict_modif_student[dept_abbrev]:
            for group_name in dict_modif_student[dept_abbrev][train_prog]:
                group = GenericGroup.objects.get(name=group_name, train_prog__abbrev=train_prog,
                                                 train_prog__department__abbrev=dept_abbrev)
                students |= set(group.student_set.all())

    for student in students:
        notif, created = NotificationsPreferences.objects.get_or_create(user=student)
        if created:
            continue
        nb_of_notified_weeks = notif.nb_of_notified_weeks
        if not nb_of_notified_weeks:
            continue
        nb_of_notified_days = 7 * nb_of_notified_weeks
        intro_text = _("Hi ") + student.first_name + "<br />"
        intro_text += _("Here are the changes of your planning for the %g following days :") % nb_of_notified_days
        intro_text += "<br /> <br />"
        groups = student.belong_to.all()
        student_changes = []
        for group in groups:
            student_changes += dict_modif_student[group.train_prog.department.abbrev][group.train_prog.abbrev][group.name]
        filtered_changes = [change for change in student_changes
                            if 0 <= (change['date'] - today).days <= nb_of_notified_days]
        if not filtered_changes:
            continue
        filtered_changes.sort(key=lambda x: (x[gettext('Date')], x[gettext('Start time')]))
        html_msg = changes_in_html_string(filtered_changes)
        send_changes_email(subject, intro_text, html_msg, to_email=student.email)


def changes_in_html_string(filtered_changes):
    msg = "<table>"
    titles = filtered_changes[0].keys()
    msg += f"<tr> "
    for title in list(titles)[1:]:
        msg += f"<th> {_(title)} </th>"
    msg+= "</tr>\n"
    for fc in filtered_changes:
        values = list(fc.values())
        mode = values[0]
        date = values[1]
        msg += f"<tr class='{mode}'>"
        msg += f"<td> {date.strftime('%d/%m/%Y')} </td>"
        for value in values[2:]:
            msg += f"<td> {value} </td>"
        msg += "</tr>\n"
    msg += "</table> <br /><br />"
    return msg


def send_changes_email(subject, intro_text, html_msg, to_email, from_email=""):

    html_message = f"""
         <html>
           <head>
            <style type="text/css">
            table {{border-collapse:collapse; margin:1em}}
            th, td {{
                border:1px solid black; 
                text-align:center;
                padding-right:10px; 
                padding-left:10px;
            }}
            .create {{background-color:lightgreen;}}
            .delete {{background-color:#ffcccb;}}
            </style>
           </head>
           <body>
             {intro_text}
             {html_msg}
           </body>
         </html>
         """
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlOpEDT.settings.local")
    django.setup()
    django.utils.translation.activate('fr')
    backup()
    send_notifications()