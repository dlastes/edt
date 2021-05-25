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


from django.db import models

from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraints.simulSlotGroupConstraint import SimulSlotGroupConstraint
from django.utils.translation import gettext as _
from TTapp.slots import slots_filter


class NoSimultaneousGroupCourses(TTConstraint):
    def enrich_model(self, ttmodel, week, ponderation=None):
        if ponderation is None:
            for sl in slots_filter(ttmodel.wdb.availability_slots, week=week):
                for bg in ttmodel.wdb.basic_groups:
                    ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                                       for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                               simultaneous_to=sl)
                                                       for c2 in ttmodel.wdb.courses_for_basic_group[bg]
                                                       & ttmodel.wdb.compatible_courses[sl2]),
                                           '<=', 1, SimulSlotGroupConstraint(sl, bg))

    def one_line_description(self):
        pass

    def __str__(self):
        return _("")


class ScheduleAllCourses(TTConstraint):
    def enrich_model(self, ttmodel, week, ponderation=None):
        pass

    def one_line_description(self):
        pass

    def __str__(self):
        return _("")
