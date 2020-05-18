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


from django.contrib.postgres.fields import ArrayField

from django.db import models

from base.timing import french_format

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraint import TTConstraint



class LunchBreaks(TTConstraint):
    """
    Ensures time for lunch in a given interval
    """

    start_time = models.PositiveSmallIntegerField()
    end_time = models.PositiveSmallIntegerField()
    lunch_length = models.PositiveSmallIntegerField()

    def enrich_model(self, ttmodel, week, ponderation=1):
        for day in days_filter(ttmodel.wdb.days, week=week):
            for group in ttmodel.wdb.basic_groups:
                expr = ttmodel.lin_expr()
                for course in self.courses.all:
                    for slot in slot_filter(ttmodel.wdb.courses_slots, week=week, day=day, starts_before=end_time, ends_after=start_time):
                        occupied_time += slot.duration*ttmodel.TT[(slot, course)]
                ttmodel.add_constraint(end_time - start_time - occupied_time, '>=', lunch_length,
                                       Constraint(constraint_type=ConstraintType.LUNCH_BREAK,
                                       groups=group, days=day)



    def one_line_description(self):
        text = f"Il faut une pause déjeuner de {self.lunch_length} minutes entre {french_format(self.start_time)} et {french_format(self.end_time)}
        return text