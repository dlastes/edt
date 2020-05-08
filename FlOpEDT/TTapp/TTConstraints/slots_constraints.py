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
from TTapp.TTconstraint import TTConstraint


class SimultaneousCourses(TTConstraint):
    """
    Force courses to start simultaneously
    """
    courses = models.ManyToManyField('base.Course', related_name='simultaneous_courses_constraints')

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['courses'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
        course_types = set(c.type for c in self.courses.all())
        nb_courses = self.courses.count()
        possible_start_times = set()
        for t in course_types:
            possible_start_times |= set(t.coursestarttimeconstraint_set.all()[0].allowed_start_times)
        for day in days_filter(ttmodel.wdb.days, week=week):
            for st in possible_start_times:
                check_var = ttmodel.add_var("check_var")
                expr = ttmodel.lin_expr()
                for c in self.courses.all():
                    possible_slots = slots_filter(ttmodel.wdb.compatible_slots[c], start_time=st, day=day)
                    for sl in possible_slots:
                        expr += ttmodel.TT[(sl, c)]
                ttmodel.add_constraint(nb_courses * check_var - expr, '==', 0,
                                       Constraint(constraint_type=ConstraintType.SIMULTANEOUS_COURSES,
                                                  courses=list(self.courses.all())))
                ttmodel.add_constraint(expr - check_var, '>=', 0,
                                       Constraint(constraint_type=ConstraintType.SIMULTANEOUS_COURSES,
                                       courses=list(self.courses.all())))

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.courses.exists():
            details.update({'courses': ', '.join([str(course) for course in self.courses.all()])})

        return view_model

    def one_line_description(self):
        return f"Les cours {self.courses.all()} doivent être simultanés !"

    class Meta:
        verbose_name_plural = "Simultaneous courses"


# Ex TTConstraints that have to be re-written.....

class AvoidBothTimes(TTConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """
    time1 = models.PositiveSmallIntegerField()
    time2 = models.PositiveSmallIntegerField()
    group = models.ForeignKey('base.Group', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'tutor'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
        fc = ttmodel.wdb.courses.filter(week=week)
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.train_progs is not None:
            fc = fc.filter(module__train_prog__in=self.train_progs)
        if self.group:
            fc = fc.filter(groups=self.group)
        slots1 = set([slot for slot in ttmodel.wdb.courses_slots
                      if slot.start_time <= self.time1 < slot.end_time])
        slots2 = set([slot for slot in ttmodel.wdb.courses_slots
                      if slot.start_time <= self.time2 < slot.end_time])
        for c1 in fc:
            for c2 in fc.exclude(id__lte=c1.id):
                for sl1 in slots1:
                    for sl2 in slots2:
                        if self.weight is not None:
                            conj_var = ttmodel.add_conjunct(
                                ttmodel.TT[(sl1, c1)],
                                ttmodel.TT[(sl2, c2)])
                            ttmodel.obj += self.local_weight() * ponderation * conj_var
                        else:
                            ttmodel.add_constraint(ttmodel.TT[(sl1, c1)]
                                                   + ttmodel.TT[(sl2, c2)],
                                                   '<=',
                                                   1,
                                                   Constraint(constraint_type=ConstraintType.AVOID_BOTH_TIME,
                                                              courses=[c1, c2], slots=[sl1, sl2]))

    def one_line_description(self):
        text = f"Pas à la fois à {french_format(self.time1)} et à {french_format(self.time2)}"
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        if self.train_progs:
            text += ' en ' + str(self.train_progs)
        return text


class LimitedStartTimeChoices(TTConstraint):
    """
    Limit the possible start times
    """

    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType',
                                    null=True,
                                    default=None,
                                    on_delete=models.CASCADE)
    possible_start_times = ArrayField(models.PositiveSmallIntegerField())

    def enrich_model(self, ttmodel, week, ponderation=1.):
        fc = ttmodel.wdb.courses.filter(week=week)
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.course_type is not None:
            fc = fc.filter(type=self.course_type)
        if self.train_progs.exists():
            fc = fc.filter(groups__train_prog__in=self.train_progs.all())
        if self.group is not None:
            fc = fc.filter(groups=self.group)
        pst = self.possible_start_times.values_list()
        relevant_sum = ttmodel.sum(ttmodel.TT[(sl, c)]
                                   for c in fc
                                   for sl in ttmodel.wdb.compatible_slots[c] if sl.start_time not in pst)
        if self.weight is not None:
            ttmodel.obj += self.local_weight() * ponderation * relevant_sum
        else:
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LIMITED_START_TIME_CHOICES,
                                              courses=fc))

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
        text += " ne peuvent avoir lieu qu'à "
        for pst in self.possible_start_times.values_list():
            text += french_format(pst) + ', '
        return text
