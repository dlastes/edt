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
from django.core.mail import EmailMessage
from pulp import LpVariable, LpConstraint, LpBinary, LpConstraintEQ, \
    LpConstraintGE, LpConstraintLE, LpAffineExpression, LpProblem, LpStatus, \
    LpMinimize, lpSum, LpStatusOptimal, LpStatusNotSolved

import pulp
from pulp import GUROBI_CMD

from django.conf import settings

from base.models import StructuralGroup, TransversalGroup,\
    Room, RoomSort, RoomType, RoomPreference, \
    Course, ScheduledCourse, UserPreference, CoursePreference, \
    Department, Module, TrainingProgramme, CourseType, \
    Dependency, TutorCost, GroupFreeHalfDay, GroupCost, Holiday, TrainingHalfDay, Pivot, \
    CourseStartTimeConstraint, TimeGeneralSettings, ModulePossibleTutors, CoursePossibleTutors, CourseAdditional, \
    RoomPonderation

from base.timing import Time, Day

import base.queries as queries

from people.models import Tutor, PhysicalPresence


from TTapp.slots import Slot, CourseSlot, slots_filter, days_filter

from django.db.models import Q, Max, F

import logging

from base.models import ModuleTutorRepartition

class RoomsWeeksDatabase(object):
    def __init__(self, department, weeks, work_copy):
        self.department = department
        self.weeks = weeks