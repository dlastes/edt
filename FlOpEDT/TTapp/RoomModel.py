#!/usr/bin/env python3
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
import os, fnmatch, re

from django.core.mail import EmailMessage

from base.models import RoomType, RoomPreference, ScheduledCourse, Department, TrainingProgramme, \
    TutorCost, GroupFreeHalfDay, GroupCost, TimeGeneralSettings, ModuleTutorRepartition, ScheduledCourseAdditional

from base.timing import Time

from people.models import Tutor

from TTapp.models import MinNonPreferedTutorsSlot, StabilizeTutorsCourses, MinNonPreferedTrainProgsSlot, \
    NoSimultaneousGroupCourses, ScheduleAllCourses, AssignAllCourses, ConsiderTutorsUnavailability, \
    MinimizeBusyDays, MinGroupsHalfDays, RespectBoundPerDay, ConsiderDependencies, ConsiderPivots, \
    StabilizeGroupsCourses
from TTapp.TTConstraint import max_weight
from TTapp.slots import slots_filter, days_filter

from TTapp.RoomsWeekDatabase import RoomsWeeksDatabase

from django.db import close_old_connections
from django.db.models import Q, Max, F

import datetime

from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint

from TTapp.ilp_constraints.constraints.slotInstructorConstraint import SlotInstructorConstraint

from FlOpEDT.decorators import timer

from TTapp.FlopModel import FlopModel, GUROBI_NAME, solution_files_path


class RoomModel(FlopModel):
    @timer
    def __init__(self, department_abbrev, weeks, work_copy=0, keep_many_solution_files=False):
        # beg_file = os.path.join('logs',"FlOpTT")
        self.department = Department.objects.get(abbrev=department_abbrev)
        self.weeks = weeks
        super(RoomModel, self).__init__(keep_many_solution_files=keep_many_solution_files)

        print("\nLet's start rooms affectation for weeks #%s" % self.weeks)
        self.work_copy = work_copy
        self.wdb = self.wdb_init()
        self.scheduled_courses = ScheduledCourse.objects.filter(type__department=self.department,
                                                                week__in=self.weeks)

        if self.warnings:
            print("Relevant warnings :")
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

    @timer
    def wdb_init(self):
        wdb = RoomsWeeksDatabase(self.department, self.weeks, self.work_copy)
        return wdb