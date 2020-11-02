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

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraint import TTConstraint
from TTapp.TTConstraints.groups_constraints import considered_basic_groups
from base.timing import Day, Time
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class NoVisio(TTConstraint):
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    groups = models.ManyToManyField('base.Group', blank=True, related_name='no_visio')
    course_types = models.ManyToManyField('base.CourseType', blank=True, related_name='no_visio')

    def enrich_model(self, ttmodel, week, ponderation=1000000):
        if not settings.VISIO_MODE:
            print("Visio Mode is not activated : ignore NoVisio constraint")
            return
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for group in considered_groups:
            # Si contrainte forte, AUCUN cours en visio, sinon seulement ceux non-indiqués Visio
            if self.weight is None:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group]
            else:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group] \
                                                  - ttmodel.wdb.visio_courses

            if self.course_types.exists():
                considered_group_courses = set(c for c in considered_group_courses
                                               if c.type in self.course_types.all())

            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.TTrooms[sl, c, None]
                            for c in considered_group_courses
                            for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day_in=days)),
                '==', 0, Constraint(constraint_type=ConstraintType.NO_VISIO, groups=group))

    def one_line_description(self):
        text = "Pas de visio"
        if self.weight is not None:
            " (sauf demande expresse)"
        if self.weekdays:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        if self.course_types.exists():
            text += ' pour les cours de type ' + ', '.join([t.name for t in self.course_types.all()])
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class VisioOnly(TTConstraint):
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    groups = models.ManyToManyField('base.Group', blank=True, related_name='visio_only')
    course_types = models.ManyToManyField('base.CourseType', blank=True, related_name='visio_only')

    def enrich_model(self, ttmodel, week, ponderation=100):
        if not settings.VISIO_MODE:
            print("Visio Mode is not activated : ignore VisioOnly constraint")
            return
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for group in considered_groups:
            # Si contrainte forte, Tous les cours en visio, sinon seulement ceux non-indiqués présentiels
            if self.weight is None:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group]
            else:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group] \
                                           - ttmodel.wdb.no_visio_courses
            if self.course_types.exists():
                considered_group_courses = set(c for c in considered_group_courses
                                               if c.type in self.course_types.all())

            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.TTrooms[sl, c, r]
                            for c in considered_group_courses
                            for r in ttmodel.wdb.course_rg_compat[c] - {None}
                            for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day_in=days)),
                '==', 0, Constraint(constraint_type=ConstraintType.VISIO_ONLY, groups=group))

    def one_line_description(self):
        text = "Tout en visio"
        if self.weight is not None:
            " (sauf demande expresse)"
        if self.weekdays:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        if self.course_types.exists():
            text += ' pour les cours de type ' + ', '.join([t.name for t in self.course_types.all()])
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class LimitGroupsPhysicalPresence(TTConstraint):
    """
    at most a given proportion of basic groups are present each half-day
    """
    percentage = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)

    def enrich_model(self, ttmodel, week, ponderation=1):
        if not settings.VISIO_MODE:
            print("Visio Mode is not activated : ignore VisioOnly constraint")
            return
        if self.train_progs.exists():
            considered_basic_groups = set(
                ttmodel.wdb.basic_groups.filter(train_prog__in=self.train_progs.all()))
        else:
            considered_basic_groups = set(ttmodel.wdb.basic_groups)
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        proportion = self.percentage / 100
        nb_of_basic_groups = len(considered_basic_groups)
        for d in days:
            for apm in [Time.AM, Time.PM]:
                ttmodel.add_constraint(
                    ttmodel.sum(ttmodel.physical_presence[g][d, apm] for g in ttmodel.wdb.basic_groups),
                    '<=', nb_of_basic_groups * proportion,
                    Constraint(constraint_type=ConstraintType.VISIO_LIMIT_GROUP_PRESENCE))

    def one_line_description(self):
        text = "Pas plus de " + str(self.percentage) + "% des groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += ", toutes promos confondues,"
        text += "sont physiquement présents chaque demie-journée"
        if self.weekdays:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        return text


class BoundVisioHalfDays(TTConstraint):
    """
    at most a given proportion of basic groups are present each half-day
    """
    nb_max = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(14)])
    nb_min = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(14)], default=0)
    groups = models.ManyToManyField('base.Group', blank=True, related_name='bound_visio_half_days')


    def enrich_model(self, ttmodel, week, ponderation=1):
        considered_groups = considered_basic_groups(self, ttmodel)
        total_nb_half_days = len(ttmodel.wdb.days) * 2
        for g in considered_groups:
            # at most nb_max half-days of visio-courses for each group
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.GBHD[g, d, apm] - ttmodel.physical_presence[g][d, apm]
                            for (d, apm) in ttmodel.physical_presence[g]),
                '<=', self.nb_max, Constraint(constraint_type=ConstraintType.BOUND_VISIO_MAX))

            # at least n_min half-days of physical-presence for each group
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.physical_presence[g][d, apm]
                            for (d, apm) in ttmodel.physical_presence[g]),
                '<=', total_nb_half_days - self.nb_min, Constraint(constraint_type=ConstraintType.BOUND_VISIO_MIN))

    def one_line_description(self):
        text = f"Au moins {self.nb_min} et au plus {self.nb_max} demie_journées de visio"
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour chaque groupe"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text