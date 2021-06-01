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
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint
from django.utils.translation import gettext as _
from TTapp.slots import slots_filter
from TTapp.TTConstraints.groups_constraints import considered_basic_groups


class NoSimultaneousGroupCourses(TTConstraint):
    """
    Only one course for each considered group on simultaneous slots
    """
    groups = models.ManyToManyField('base.Group', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):
        relevant_slots = slots_filter(ttmodel.wdb.availability_slots, week=week)
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        for sl in relevant_slots:
            for bg in relevant_basic_groups:
                relevant_sum = ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                           for sl2 in slots_filter(ttmodel.wdb.courses_slots,
                                                                   simultaneous_to=sl)
                                           for c2 in ttmodel.wdb.courses_for_basic_group[bg]
                                           & ttmodel.wdb.compatible_courses[sl2])
                if self.weight is None:
                    ttmodel.add_constraint(relevant_sum,
                                           '<=', 1, SimulSlotGroupConstraint(sl, bg))
                else:
                    two_courses = ttmodel.add_floor(relevant_sum, 2, len(relevant_slots))
                    ttmodel.add_to_group_cost(bg, self.local_weight() * ponderation * two_courses, week)

    def one_line_description(self):
        text = f"Les cours "
        if self.groups.exists():
            text += ' des groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " de chaque groupe"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        text += " ne peuvent pas être simultanés"
        return text

    def __str__(self):
        return _("No simultaneous courses for one group")


class ScheduleAllCourses(TTConstraint):
    """
    The considered courses are scheduled, and only once
    """
    modules = models.ManyToManyField('base.Module', blank=True)
    groups = models.ManyToManyField('base.Group',
                                    blank=True)
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    course_types = models.ManyToManyField('base.CourseType', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):
        relevant_basic_groups = considered_basic_groups(self, ttmodel)
        considered_courses = set(c for bg in relevant_basic_groups
                                 for c in ttmodel.wdb.courses_for_basic_group[bg])
        max_slots_nb = len(ttmodel.wdb.courses_slots)
        if self.modules.exists():
            considered_courses = set(c for c in considered_courses if c.module in self.modules.all())
        if self.tutors.exists():
            considered_courses = set(c for c in considered_courses if c.tutor in self.tutors.all())
        if self.course_types.exists():
            considered_courses = set(c for c in considered_courses if c.type in self.course_types.all())
        for c in considered_courses:
            relevant_sum = ttmodel.sum([ttmodel.TT[(sl, c)] for sl in ttmodel.wdb.compatible_slots[c]])
            if self.weight is None:
                ttmodel.add_constraint(relevant_sum,
                                       '==', 1,
                                       CourseConstraint(c))
            else:
                not_scheduled = ttmodel.add_floor(relevant_sum, 1, max_slots_nb)
                ttmodel.add_to_generic_cost((1-not_scheduled) * self.local_weight() * ponderation, week)

    def one_line_description(self):
        text = f"Planifie tous les cours "
        if self.groups.exists():
            text += ' des groupes ' + ', '.join([group.name for group in self.groups.all()])
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.modules.exists():
            text += ' de : ' + ', '.join([str(module) for module in self.modules.all()])
        if self.course_types.exists():
            text += f" de type" + ', '.join([t.name for t in self.course_types.all()])
        if self.tutors.exists():
            text += ' de ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        return text

    def __str__(self):
        return _("Schedule once every considered course")



