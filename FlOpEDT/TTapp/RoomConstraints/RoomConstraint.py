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

from base.models import TimeGeneralSettings
from django.core.validators import MinValueValidator, MaxValueValidator

from django.utils.translation import gettext_lazy as _

from django.db import models

from FlOpEDT.decorators import timer

from TTapp.FlopConstraint import FlopConstraint


class RoomConstraint(FlopConstraint):
    """
    Abstract parent class of specific constraints that users may define

    Attributes:
        department : the department concerned by the constraint. Has to be filled.
        weeks : the weeks for which the constraint should be applied. All if None.
        weight : from 1 to max_weight if the constraint is optional, depending on its importance
                 None if the constraint is necessary
        is_active : usefull to de-activate a Constraint just before the generation
    """
    class Meta:
        abstract = True

    @timer
    def enrich_model(self, room_model, week, ponderation=1):
        raise NotImplementedError

    @staticmethod
    def get_courses_queryset_by_parameters(room_model, week,
                                           train_prog=None,
                                           module=None,
                                           basic_group=None,
                                           group=None,
                                           course_type=None,
                                           room_type=None,
                                           tutor=None):
        """
        Filter courses depending on constraints parameters
        :parameter basic_group : if not None, return all courses that has one group connected to group
        """
        courses_qs = room_model.courses.filter(course__week=week)
        courses_filter = {}

        if train_prog is not None:
            courses_filter['course__module__train_prog'] = train_prog

        if module is not None:
            courses_filter['course__module'] = module

        if basic_group is not None:
            courses_filter['course__groups__in'] = basic_group.connected_groups()

        if group is not None:
            courses_filter['course__groups'] = group

        if course_type is not None:
            courses_filter['course__type'] = course_type

        if room_type is not None:
            courses_filter['course__room_type'] = room_type

        if tutor is not None:
            courses_filter['course__id__in'] = [c.course.id for c in courses_qs
                                                if c.course.tutor == tutor
                                                or tutor in c.course.supp_tutor.all()]
        return courses_qs.filter(**courses_filter)

    def get_courses_queryset_by_attributes(self, room_model, week, **kwargs):
        """
        Filter courses depending constraint attributes
        """
        for attr in ['train_prog', 'module', 'group', 'course_type', 'tutor', 'room_type']:
            if hasattr(self, attr) and attr not in kwargs:
                kwargs[attr] = getattr(self, attr)
        return self.get_courses_queryset_by_parameters(room_model, week, **kwargs)


class LimitedRoomChoices(RoomConstraint):
    """
    Limit the possible rooms for the courses
    Attributes are cumulative :
        limit the room choice for the courses of this/every tutor, of this/every module, for this/every group ...
    """
    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               blank=True,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.StructuralGroup',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    possible_rooms = models.ManyToManyField('base.Room',
                                            related_name="limited_rooms")

    def enrich_model(self, room_model, week, ponderation=1.):
        fc = self.get_courses_queryset_by_attributes(room_model, week)
        possible_rooms = self.possible_rooms.values_list()
        if self.tutor is None:
            relevant_var_dic = ttmodel.TTrooms
        else:
            relevant_var_dic = {(sl, c, rg): ttmodel.add_conjunct(ttmodel.TTrooms[(sl, c, rg)],
                                                                  ttmodel.TTinstructors[sl, c, self.tutor])
                            for c in fc
                            for sl in ttmodel.wdb.compatible_slots[c]
                            for rg in ttmodel.wdb.course_rg_compat[c] if rg not in possible_rooms }
        relevant_sum = ttmodel.sum(relevant_var_dic[(sl, c, rg)]
                                   for c in fc
                                   for sl in ttmodel.wdb.compatible_slots[c]
                                   for rg in ttmodel.wdb.course_rg_compat[c] if rg not in possible_rooms)
        if self.weight is not None:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum, week=week)
        else:
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LIMITED_ROOM_CHOICES,
                                              instructors=self.tutor, groups=self.group, modules=self.module,
                                              rooms=possible_rooms))

    def one_line_description(self):
        text = "Les "
        if self.course_type:
            text += str(self.course_type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_progs.exists():
            text += ' en ' + str(self.train_progs.all())
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'en salle "
        for sl in self.possible_rooms.values_list():
            text += str(sl) + ', '
        return text