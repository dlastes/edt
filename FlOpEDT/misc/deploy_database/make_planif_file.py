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

from openpyxl import load_workbook

from base.models import Room, RoomType, RoomGroup, TrainingProgramme,\
    Group, Module, GroupType, Period, Time, Day, Slot, CourseType, EdtVersion, UserPreference

from openpyxl.styles import PatternFill, Font, colors

bookname='MyFlOp/IUT_special_apps/ExtractPlanif/empty_planif_file.xlsx'

def make_planif_file(bookname=bookname):

    book = load_workbook(filename=bookname)

    # We go through each period and create a sheet for each period

    for p in Period.objects.all():
        basic_sheet = book['empty']
        new = book.copy_worksheet(basic_sheet)
        new.title = p.name
        sheet = book[p.name]

        ################ Writing weeks ################

        WEEK_ROW = 3
        WEEK_COL = 4

        if p.starting_week < p.ending_week:

            for i in range(p.starting_week, p.ending_week+1):

                sheet.cell(row=WEEK_ROW, column=WEEK_COL).value = i
                WEEK_COL += 1

        else:

            for i in range(p.starting_week, 53):

                sheet.cell(row=WEEK_ROW, column=WEEK_COL).value = i
                WEEK_COL += 1

            for i in range(1, p.ending_week+1):

                sheet.cell(row=WEEK_ROW, column=WEEK_COL).value = i
                WEEK_COL += 1

        COURSE_ROW = 4

        ################ Writing each course ################

        for c in Module.objects.filter(period=p):

            sheet.cell(row=COURSE_ROW, column=1).value = c.abbrev

            for ct in CourseType.objects.all():

                for gt in ct.group_types.all():

                    sheet.cell(row=COURSE_ROW, column=2).value = ct.name
                    sheet.cell(row=COURSE_ROW, column=3).value = gt.name

                COURSE_ROW += 1

            ################ Separating each course with a black line ################

            for ce in range(1,27):
                sheet.cell(row=COURSE_ROW, column=ce).fill = PatternFill(start_color='00000000', end_color='00000000',
                                                                         fill_type='solid')
            for ce in range(2,4):
                sheet.cell(row=COURSE_ROW, column=ce).font = Font(color=colors.BLACK)
                sheet.cell(row=COURSE_ROW, column=ce).value = "Not None"

            COURSE_ROW +=1

    book.remove(basic_sheet)

    filename='MyFlOp/IUT_special_apps/ExtractPlanif/planif_file.xlsx'
    book.save(filename=filename)
