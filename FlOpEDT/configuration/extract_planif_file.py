# coding: utf-8
# !/usr/bin/python

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

import os
import sys
from openpyxl import *

from base.weeks import actual_year
from base.models import Group, Module, Course, CourseType, RoomType,\
    TrainingProgramme, Dependency, Period, Department, CoursePossibleTutors
from people.models import Tutor, UserDepartmentSettings
from people.tutor import fill_default_user_preferences
from misc.assign_colors import assign_module_color


def ReadPlanifWeek(department, book, feuille, week, year):
    sheet = book[feuille]
    period=Period.objects.get(name=feuille, department=department)

    # lookup week row:

    # lookup week column
    wc = 1
    for wr in [1]:
        while wc < 50:
            wc += 1
            sem = sheet.cell(row=wr, column=wc).value
            if sem == float(week):
                WEEK_COL = wc
                break
    try:
        WEEK_COL += 0
    except UnboundLocalError:
        print('Pas de semaine %s en %s' % (week, feuille))
        return
    print("Semaine %s de %s : colonne %g" % (week, feuille, WEEK_COL))

    row = 4
    module_COL = 1
    nature_COL = 3
    duree_COL = 4
    prof_COL = 5
    salle_COL = 6
    group_COL = 7
    sumtotal = 0
    while 1:
        row += 1
        is_total = sheet.cell(row=row, column=group_COL).value
        if is_total == "TOTAL":
            # print "Sem %g de %s - TOTAL: %g"%(week, feuille,sumtotal)
            break

        Cell = sheet.cell(row=row, column=WEEK_COL)
        N = Cell.value
        if N is None:
            continue

        try:
            salle = sheet.cell(row=row, column=salle_COL).value
            module = sheet.cell(row=row, column=module_COL).value
            N = float(N)
            # handle dark green lines - Vert fonce
            assert isinstance(salle, str) and salle is not None
            if salle == "Type de Salle":
                nominal = int(N)
                if N != nominal:
                    print('Valeur decimale ligne %g de %s, semaine %g : on la met a 1 !' % (row, feuille, week))
                    nominal = 1
                    # le nominal est le nombre de cours par groupe (de TP ou TD)
                if Cell.comment:
                    comments = Cell.comment.text.replace(' ', '').replace('\n', '').replace(',', ';').split(';')
                else:
                    comments = []

                sumtotal += nominal
                continue
            try:
                comments = comments
            except:
                comments = []
            # handle light green lines - Vert clair
            MODULE = Module.objects.get(abbrev=module, period=period)
            PROMO = MODULE.train_prog
            nature = sheet.cell(row=row, column=nature_COL).value
            salle = sheet.cell(row=row, column=salle_COL).value
            prof = sheet.cell(row=row, column=prof_COL).value
            grps = sheet.cell(row=row, column=group_COL).value
            COURSE_TYPE = CourseType.objects.get(name=nature, department=department)
            ROOMTYPE = RoomType.objects.get(name=salle, department=department)
            supp_profs = []
            possible_profs = []
            if prof is None:
                TUTOR, created = Tutor.objects.get_or_create(username='---')
                if created:
                    TUTOR.save()
                    fill_default_user_preferences(TUTOR)
                    UserDepartmentSettings(user=TUTOR, department=department).save()
            else:
                assert isinstance(prof, str) and prof is not None
                prof = prof.replace(' ', '')
                if '|' in prof:
                    possible_profs = prof.split("|")
                    TUTOR = None
                else:
                    profs = prof.split(";")
                    prof = profs[0]
                    TUTOR = Tutor.objects.get(username=prof)
                    supp_profs = profs[1:]

            if Cell.comment:
                local_comments = Cell.comment.text.replace(' ', '').replace('\n', '').replace(',', ';').split(';')
            else:
                local_comments = []

            if isinstance(grps, int) or isinstance(grps, float):
                grps = str(int(grps))
            if not grps:
                grps = []
            else:
                grps = grps.replace(' ', '').replace(',', ';').split(';')
            groups = [str(g) for g in grps]

            GROUPS = list(Group.objects.filter(name__in=groups, train_prog=PROMO))
            if GROUPS == []:
                GROUPS = list(Group.objects.filter(name='CE', train_prog=PROMO))

            N=int(N)

            for i in range(N):
                GROUP = GROUPS[i % len(GROUPS)]
                C = Course(tutor=TUTOR, type=COURSE_TYPE, module=MODULE, group=GROUP, week=week, year=year,
                           room_type=ROOMTYPE)
                C.save()
                if supp_profs != []:
                    SUPP_TUTORS = Tutor.objects.filter(username__in=supp_profs)
                    for sp in SUPP_TUTORS:
                        C.supp_tutor.add(sp)
                    C.save()
                if possible_profs != []:
                    cpt = CoursePossibleTutors(course=C)
                    cpt.save()
                    for pp in possible_profs:
                        t = Tutor.objects.get(username=pp)
                        cpt.possible_tutors.add(t)
                    cpt.save()
                for after_type in [x for x in comments + local_comments if x[0] == 'A']:
                    try:
                        n = int(after_type[1])
                        s = 2
                    except ValueError:
                        n = 1
                        s = 1
                    course_type = after_type[s:]
                    courses = Course.objects.filter(type__name=course_type, module=MODULE, week=week, year=year,
                                                    group__in = GROUP.ancestor_groups() |
                                                                 {GROUP} |
                                                                 GROUP.descendants_groups())
                    for course in courses[:n]:
                        P = Dependency(course1=course, course2=C)
                        P.save()

            if 'D' in comments or 'D' in local_comments and N >= 2:
                for GROUP in GROUPS:
                    relevant_courses = Course.objects.filter(type=COURSE_TYPE, module=MODULE, group=GROUP, year=year,
                                                  week=week)
                    for i in range(N//2-1):
                        P = Dependency(course1=relevant_courses[2*i], course2=relevant_courses[2*i+1], successive=True)
                        P.save()
            if 'ND' in comments or 'ND' in local_comments  and N >= 2:
                for GROUP in GROUPS:
                    relevant_courses = Course.objects.filter(type=COURSE_TYPE, module=MODULE, group=GROUP, year=year,
                                                  week=week)
                    P = Dependency(course1=relevant_courses[0], course2=relevant_courses[1], ND=True)
                    P.save()
        except Exception as e:
            raise Exception(f"Exception ligne {row}, semaine {week} de {feuille} : {module} \n")


def extract_period(department, book, period, year):
    if period.starting_week < period.ending_week:
        if period.ending_week < 31:
            year += 1
        for week in range(period.starting_week, period.ending_week + 1):
            ReadPlanifWeek(department, book, period.name, week, year)
            print(week, year)

    else:
        for week in range(period.starting_week, 53):
            ReadPlanifWeek(department, book, period.name, week, year)
        for week in range(1, period.ending_week + 1):
            ReadPlanifWeek(department, book, period.name, week, year+1)


def extract_planif(department, bookname=None):
    '''
    Generate the courses from bookname; the school year starts in actual_year
    '''
    if bookname is None:
        bookname = 'media/configuration/planif_file_'+department.abbrev+'.xlsx'
    book = load_workbook(filename=bookname, data_only=True)
    for period in Period.objects.filter(department=department):
        extract_period(department, book, period, actual_year)
    assign_module_color(department)


def extract_planif_from_week(week, year, department, bookname=None):
    '''
    Generate the courses from bookname; the school year starts in actual_year
    '''
    if bookname is None:
        bookname = 'media/configuration/planif_file_'+department.abbrev+'.xlsx'
    book = load_workbook(filename=bookname, data_only=True)
    if year == actual_year:
        for period in Period.objects.filter(department=department):
            if period.starting_week < period.ending_week:
                for w in range(max(week, period.starting_week), period.ending_week + 1):
                    ReadPlanifWeek(department, book, period.name, w, actual_year)
            else:
                for w in range(max(week, period.starting_week), 53):
                    ReadPlanifWeek(department, book, period.name, w, actual_year)
                for w in range(1, period.ending_week + 1):
                    ReadPlanifWeek(department, book, period.name, w, actual_year + 1)
    elif year == actual_year + 1:
        for period in Period.objects.filter(department=department):
            if period.starting_week < period.ending_week:
                for w in range(max(week, period.starting_week), period.ending_week + 1):
                    ReadPlanifWeek(department, book, period.name, w, year)
            else:
                for w in range(week, period.ending_week + 1):
                    ReadPlanifWeek(department, book, period.name, w, year)

    else:
        print("Are you sure of year value?")
