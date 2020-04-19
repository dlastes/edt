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

import inspect
import importlib
from functools import wraps

from django.conf import settings
from django.utils.functional import lazy

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

from django.db import models

from django.db.models import F

# from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _

from base.models import Time, Department, Module, Group, Day, TimeGeneralSettings

from people.models import Tutor

from TTapp.helpers.minhalfdays import MinHalfDaysHelperGroup, MinHalfDaysHelperModule, MinHalfDaysHelperTutor

from TTapp.iic.constraint_type import ConstraintType
from TTapp.iic.constraints.constraint import Constraint
from TTapp.slots import Slot, days_filter, slots_filter


max_weight = 8


class TTConstraint(models.Model):

    department = models.ForeignKey(Department, null=True, on_delete=models.CASCADE)
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        null=True,

        default=None,
        blank=True)
    year = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    weight = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(max_weight)],
        null=True, default=None, blank=True)
    comment = models.CharField(max_length=100, null=True, default=None, blank=True)
    is_active = models.BooleanField(verbose_name='Contrainte active?', default=True)

    def local_weight(self):
        return float(self.weight) / max_weight

    class Meta:
        abstract = True

    def enrich_model(self, ttmodel, week, ponderation=1):
        raise NotImplementedError

    def full_name(self):
        # Return a human readable constraint name
        return str(self)

    def description(self):
        # Return a human readable constraint name
        return self.__doc__ or str(self)

    def get_viewmodel(self):
        #
        # Return a dictionnary with view-related data
        #
        if self.train_progs.exists():
            train_prog_value = ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            train_prog_value = 'All'

        if self.week:
            week_value = f"{self.week} ({self.year})"
        else:
            week_value = 'All'

        return {
            'model': self.__class__.__name__,
            'pk': self.pk,
            'is_active': self.is_active,
            'name': self.full_name(),
            'description': self.description(),
            'explanation': self.one_line_description(),
            'comment': self.comment,
            'details': {
                'train_progs': train_prog_value,
                'week': week_value,
                'weight': self.weight,
                }
            }

    def one_line_description(self):
        # Return a human readable constraint name with its attributes
        raise NotImplementedError

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        return ['train_progs', 'department',]


class LimitCourseTypeTimePerPeriod(TTConstraint):  # , pond):
    """
    Bound the number of courses of type 'type' per day/half day
    """
    course_type = models.ForeignKey('base.CourseType', on_delete=models.CASCADE)
    max_hours = models.PositiveSmallIntegerField()
    modules = models.ManyToManyField('base.Module',
                                   blank=True,
                                   related_name="Course_type_limits")
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="Course_type_limits")
    FULL_DAY = 'fd'
    HALF_DAY = 'hd'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (HALF_DAY, 'Half day'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)

    def get_courses_queryset(self, ttmodel,  train_prog=None, tutor=None, module=None):
        """
        Filter courses depending on constraints parameters
        """
        courses_qs = ttmodel.wdb.courses.filter(type=self.course_type)
        courses_filter = {}

        if tutor is not None:
            courses_filter['tutor'] = tutor

        if module is not None:
            courses_filter['module'] = module

        if train_prog is not None:
            courses_filter['group__train_prog'] = train_prog

        return courses_qs.filter(**courses_filter)

    def register_expression(self, ttmodel, period_by_day, ponderation, train_prog=None, tutor=None, module=None):

        courses = set(self.get_courses_queryset(ttmodel, train_prog, tutor, module))

        for day, period in period_by_day:
            expr = ttmodel.lin_expr()
            if period is None:
                slots = slots_filter(ttmodel.wdb.slots, day=day)
            else:
                slots = slots_filter(ttmodel.wdb.slots, day=day, apm=period)

            for slot in slots:
                for course in courses & ttmodel.wdb.compatible_courses[slot]:
                    expr += ttmodel.TT[(slot, course)] * self.course_type.duration

            if self.weight is not None:
                var = ttmodel.add_floor(
                                'limit course type per period',
                                expr,
                                int(self.max_hours * 60) + 1, 3600*24)
                ttmodel.obj += self.local_weight() * ponderation * var
            else:
                """
                name = 'Max_%d_hours_of_%s_per_%s_%s_%s%g' % (self.max_hours,
                                                              self.course_type,
                                                              self.period,
                                                              day,
                                                              period if period is not None else '',
                                                              ttmodel.constraint_nb)
                """
                ttmodel.add_constraint(expr, '<=', self.max_hours*60,
                                       Constraint(constraint_type=ConstraintType.MAX_HOURS,
                                                  modules=self.course_type, days=day))

    def enrich_model(self, ttmodel, week, ponderation=1.):

        if self.period == self.FULL_DAY:
            periods = [None]
        else:
            periods = ttmodel.possible_apms

        period_by_day = []
        for day in days_filter(ttmodel.wdb.days, week=week):
            for period in periods:
                period_by_day.append((day, period,))

        try:
            if self.tutors.count():
                for tutor in self.tutors.all():
                    self.register_expression(ttmodel, period_by_day, ponderation, tutor=tutor)
            elif self.modules.count():
                for module in self.modules.all():
                    self.register_expression(ttmodel, period_by_day, ponderation, module=module)
            elif self.train_progs.count():
                for train_prog in self.train_progs.all():
                    self.register_expression(ttmodel, period_by_day, ponderation, train_prog=train_prog)
            else:
                self.register_expression(ttmodel, period_by_day, ponderation)
        except ValueError:
            self.register_expression(ttmodel, period_by_day, ponderation)

    def full_name(self):
        return "Limit Course Type Per Period"

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['modules', 'tutors', 'course_type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        if self.course_type:
            type_value = self.course_type.name
        else:
            type_value = 'All'

        if self.modules:
            module_value = ', '.join([module.abbrev for module in self.modules.all()])
        else:
            module_value = 'All'

        if self.tutors:
            tutor_value = ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            tutor_value = 'All'

        view_model['details'].update({
            'course_type': type_value,
            'tutor': tutor_value,
            'modules': module_value, })

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_hours) + ' heures de ' + str(self.course_type)
        if self.modules.exists():
            text += " de " + ', '.join([module.abbrev for module in self.modules.all()])
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demi-journée'
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])

        return text


class Stabilize(TTConstraint):
    """
    Allow to realy stabilize the courses of a category
    If general is true, none of the other (except week and work_copy) is
    relevant.
    --> In this case, each course c placed:
        - in a unused slot costs 1,
        - in a unused half day (for tutor and/or group) cost ponderation
    If general is False, it Fixes train_prog/tutor/group courses (or tries to if
    self.weight)
    """
    general = models.BooleanField(
        verbose_name='Stabiliser tout?',
        default=False)

    group = models.ForeignKey('base.Group', null=True, default=None, on_delete=models.CASCADE)
    module = models.ForeignKey('base.Module', null=True, default=None, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType', null=True, default=None, on_delete=models.CASCADE)
    work_copy = models.PositiveSmallIntegerField(default=0)
    fixed_days = ArrayField(models.CharField(max_length=2,
                                             choices=Day.CHOICES), blank=True, null=True)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'module', 'tutor', 'type'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
        sched_courses = ttmodel.wdb.sched_courses.filter(work_copy=self.work_copy, course__week=week)
        if self.fixed_days:
            pass
            # Attention, les fixed_days doivent être des couples jour-semaine!!!!
            # for day in days_filter(self.fixed_days.all(), week=week):
            #     for sc in sched_courses.filter(slot__jour=day):
            #         ttmodel.add_constraint(ttmodel.TT[(sc.slot, sc.course)], '==', 1)
            #     for sc in sched_courses.exclude(slot__day=day):
            #         for sl in ttmodel.wdb.slots.filter(day=day):
            #             ttmodel.add_constraint(ttmodel.TT[(sl, sc.course)], '==', 0)

        if self.general:
            # nb_changements_I=dict(zip(ttmodel.wdb.instructors,[0 for i in ttmodel.wdb.instructors]))
            for sl in slots_filter(ttmodel.wdb.slots, week=week):
                for c in ttmodel.wdb.compatible_courses[sl]:
                    if not sched_courses.filter(start_time__lt=sl.end_time,
                                                start_time__gt=sl.start_time - F('course__type__duration'),
                                                day=sl.day,
                                                course__tutor=c.tutor):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]
                        # nb_changements_I[c.tutor]+=ttmodel.TT[(sl,c)]
                    if not sched_courses.filter(course__tutor=c.tutor,
                                                day=sl.day):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]
                        # nb_changements_I[i]+=ttmodel.TT[(sl,c)]
                    if not sched_courses.filter(course__group=c.group,
                                                day=sl.day):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]
        else:
            fc = ttmodel.wdb.courses.filter(week=week)
            if self.tutor is not None:
                fc = fc.filter(tutor=self.tutor)
            if self.type is not None:
                fc = fc.filter(type=self.type)
            if self.train_progs.exists():
                fc = fc.filter(group__train_prog__in=self.train_progs.all())
            if self.group:
                fc = fc.filter(group=self.group)
            if self.module:
                fc = fc.filter(module=self.module)
            for c in fc:
                sched_c = ttmodel.wdb \
                    .sched_courses \
                    .get(course=c,
                         work_copy=self.work_copy)
                chosen_slot = Slot(start_time=sched_c.start_time, course_type=sched_c.course.type,
                                   day=sched_c.day)
                chosen_roomgroup = sched_c.room
                if self.weight is not None:
                    ttmodel.obj -= self.local_weight() \
                                   * ponderation * ttmodel.TT[(chosen_slot, c)]

                else:
                    for slot in ttmodel.wdb.slots & ttmodel.wdb.compatible_slots[c]:
                        if not slot.is_simultaneous_to(chosen_slot):
                            ttmodel.add_constraint(ttmodel.TT[(slot, c)],
                                                   '==',
                                                   0,
                                                   Constraint(constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL,
                                                              courses=fc, slots=slot))


    def one_line_description(self):
        text = "Minimiser les changements"
        if self.type:
            text += " pour les " + str(self.type)
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.train_progs.count():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.group:
            text += ' du groupe ' + str(self.group)
        text += ': copie ' + str(self.work_copy)
        return text


class MinGroupsHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    You have to chose EITHER tutor OR group OR module
    Optional for tutors : if 2 courses only, possibility to join it
    """
    groups = models.ManyToManyField('base.Group', blank=True)



    def enrich_model(self, ttmodel, week, ponderation=1):


        if self.groups.exists():
            helper = MinHalfDaysHelperGroup(ttmodel, self, week, ponderation)
            for group in self.groups.all():
                helper.enrich_model(group=group)

        else:
            print("MinGroupHalfDays must have at least one group  --> Ignored")
            return


    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.groups.exists():
            details.update({'groups': ', '.join([group.name for group in self.groups.all()])})

        return view_model


    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.groups.exists():
            text += ' du(des) groupe(s) : ' + ', '.join([group.name for group in self.groups.all()])

        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])

        return text


class MinTutorsHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    Optional: if 2 courses only, possibility to join it
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    join2courses = models.BooleanField(
        verbose_name='If a tutor has 2 or 4 courses only, join it?',
        default=False)

    def enrich_model(self, ttmodel, week, ponderation=1):

        if self.tutors.exists():
            helper = MinHalfDaysHelperTutor(ttmodel, self, week, ponderation)
            for tutor in self.tutors.all():
                if tutor in ttmodel.wdb.instructors:
                    helper.enrich_model(tutor=tutor)

        else:
            print("MinTutorsHalfDays must have at least one tutor --> Ignored")
            return


    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        return view_model


    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.tutors.exists():
            text += ' de : ' + ', '.join([tutor.username for tutor in self.tutors.all()])

        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])

        return text


class MinModulesHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    """
    modules = models.ManyToManyField('base.Module', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):

        if self.modules.exists():
            helper = MinHalfDaysHelperModule(ttmodel, self, week, ponderation)
            for module in self.modules.all():
                helper.enrich_model(module=module)

        else:
            print("MinHalfDays must have at least  one module --> Ignored")
            return


    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.modules.exists():
            details.update({'modules': ', '.join([module.name for module in self.modules.all()])})

        return view_model


    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.modules.exists():
            text += ' de : ' + ', '.join([str(module) for module in self.modules.all()])

        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])

        return text


class MinNonPreferedTutorsSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots for tutors
    """
    tutors = models.ManyToManyField('people.Tutor',
                                    related_name='min_non_prefered_tutors_slots_constraints')

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutors'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=None):
        if ponderation is None:
            ponderation = ttmodel.min_ups_i
        if self.tutors.exists():
            tutors = set(t for t in ttmodel.wdb.instructors if t in self.tutors.all())
        else:
            tutors = set(ttmodel.wdb.instructors)
        for sl in ttmodel.wdb.slots:
            for tutor in tutors:
                filtered_courses = set(c for c in ttmodel.wdb.possible_courses[tutor] if c.week == week)
                for c in filtered_courses & ttmodel.wdb.compatible_courses[sl]:
                    cost = (float(self.weight) / max_weight) \
                           * ponderation * ttmodel.TTinstructors[(sl, c, tutor)] \
                           * ttmodel.unp_slot_cost[tutor][sl]
                    #ttmodel.add_to_slot_cost(sl, cost)
                    ttmodel.add_to_inst_cost(tutor, cost, week=week)

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.tutors.exists():
            text += ' de ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += ' de tous les profs.'
        return text


class MinNonPreferedTrainProgsSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots for tutors
    """
    def enrich_model(self, ttmodel, week, ponderation=None):
        if ponderation is None:
            ponderation = ttmodel.min_ups_c
        if self.train_progs.exists():
            train_progs = set(tp for tp in self.train_progs.all() if tp in ttmodel.train_prog)
        else:
            train_progs = set(ttmodel.train_prog)
        for sl in ttmodel.wdb.slots:
            for train_prog in train_progs:
                filtered_courses = set(ttmodel.wdb.courses.filter(group__train_prog=train_prog,
                                                                              week=week))
                basic_groups = ttmodel.wdb.basic_groups.filter(train_prog=train_prog)
                for g in basic_groups:
                    for c in filtered_courses & ttmodel.wdb.compatible_courses[sl]:
                        if c.group in ttmodel.wdb.all_groups_of[g]:
                            cost = self.local_weight() \
                                   * ponderation * ttmodel.TT[(sl, c)] \
                                   * ttmodel.unp_slot_cost_course[c.type,
                                                                  train_prog][sl]
                            ttmodel.add_to_group_cost(g, cost, week=week)
                            #ttmodel.add_to_slot_cost(sl, cost)

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.train_progs.exists():
            text += ' des groupes de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += ' de toutes les promos.'
        return text



# From Custom


class MinimizeBusyDays(TTConstraint):
    """
    This class is a template for writing your own custom contraint.

    The module can contains several custom constraints.
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=None):
        """
        Minimize the number of busy days for tutor with cost
        (if it does not overcome the bound expressed in pref_hours_per_day)
        """
        if ponderation is None:
            ponderation = ttmodel.min_bd_i

        for tutor in self.tutors.all():
            slot_by_day_cost = 0
            # need to be sorted
            courses_hours = sum(c.type.duration
                                for c in (ttmodel.wdb.courses_for_tutor[tutor]
                                          | ttmodel.wdb.courses_for_supp_tutor[tutor])
                                & ttmodel.wdb.courses_by_week[week]) \
                            / 60
            nb_days = 5
            frontier_pref_busy_days = [tutor.pref_hours_per_day * d for d in range(nb_days - 1, 0, -1)]

            for fr in frontier_pref_busy_days:
                if courses_hours <= fr:
                    slot_by_day_cost *= 2
                    slot_by_day_cost += ttmodel.IBD_GTE[week][nb_days][tutor]
                    nb_days -= 1
                else:
                    break
            ttmodel.add_to_inst_cost(tutor, ponderation * slot_by_day_cost, week=week)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "MinimizeBusyDays online description"

    class Meta:
        verbose_name_plural = "Minimize busy days"


class RespectBoundPerDay(TTConstraint):
    """
    Respect the max_hours_per_day declared
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):
        """
        Minimize the number of busy days for tutor with cost
        (if it does not overcome the bound expressed in pref_hours_per_day)
        """
        for tutor in self.tutors.all():
            for d in days_filter(ttmodel.wdb.days, week=week):
                ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] * c.type.duration / 60
                                                   for c in ttmodel.wdb.courses_for_tutor[tutor] if c.week == week
                                                   for sl in slots_filter(ttmodel.wdb.slots, day=d)
                                                   & ttmodel.wdb.compatible_slots[c]),
                                       '<=',
                                       tutor.max_hours_per_day,
                                       Constraint(constraint_type=ConstraintType.BOUND_HOURS_PER_DAY,
                                                  instructors=tutor,
                                                  days=d))

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "RespectBoundPerDay online description"

    class Meta:
        verbose_name_plural = "Respecter les limites horaires"


# A tester!
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
        types = set(c.type for c in self.courses.all())
        nb_courses = self.courses.count()
        possible_start_times = set()
        for t in types:
            possible_start_times |= set(t.coursestarttimeconstraint_set.all()[0].allowed_start_times)
        for day in ttmodel.wdb.days:
            for st in possible_start_times:
                check_var = ttmodel.add_var("check_var")
                expr = ttmodel.lin_expr()
                for c in self.courses.all():
                    possible_slots = slots_filter(ttmodel.wdb.compatible_slots[c], start_time=st, day=day)
                    for sl in possible_slots:
                        expr += ttmodel.TT[(sl, c)]
                ttmodel.add_constraint(nb_courses * check_var - expr, '==', 0,
                                       Constraint(constraint_type=ConstraintType.COURS_SIMULTANES,
                                                  courses=list(self.courses.all())))
                ttmodel.add_constraint(expr - check_var, '>=', 0,
                                       Constraint(constraint_type=ConstraintType.COURS_SIMULTANES,
                                       courses=list(self.courses.all())))
            # A compléter, l'idée est que si les cours ont le même prof, ou des
            # groupes qui se superposent, il faut veiller à supprimer les core
            # constraints qui empêchent que les cours soient simultanés...
            # same_tutor = (self.course1.tutor == self.course2.tutor)
            # if same_tutor and self.course1.tutor in ttmodel.wdb.instructors:
            #     for sl2 in ttmodel.wdb.slots_intersecting[sl] - {sl}:
            #         name_tutor_constr_sl2 = 'simul_slots' + str(self.course1.tutor) + '_' + str(sl) + '_' + str(sl2)
            #         tutor_constr = ttmodel.get_constraint(name_tutor_constr_sl2)
            #         print(tutor_constr)
            #         if ttmodel.var_coeff(var1, tutor_constr) == 1:
            #             ttmodel.change_var_coeff(var1, tutor_constr, 0)
            # for bg in ttmodel.wdb.basic_groups:
            #     bg_groups = ttmodel.wdb.all_groups_of[bg]
            #     if self.course1.group in bg_groups and self.course2.group in bg_groups:
            #         for sl2 in ttmodel.wdb.slots_intersecting[sl] - {sl}:
            #             name_group_constr_sl2 = 'simul_slots' + bg.full_name() + '_' + str(sl) + '_' + str(sl2)
            #             group_constr = ttmodel.get_constraint(name_group_constr_sl2)
            #             if ttmodel.var_coeff(var1, group_constr) == 1:
            #                 ttmodel.change_var_coeff(var1, group_constr, 0)

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

    def enrich_model(self, ttmodel, ponderation=1):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.train_prog is not None:
            fc = fc.filter(group__train_prog=self.train_prog)
        if self.group:
            fc = fc.filter(group=self.group)
        slots1 = set([slot for slot in ttmodel.wdb.slots if slot.start_time <= self.time1 < slot.end_time])
        slots2 = set([slot for slot in ttmodel.wdb.slots if slot.start_time <= self.time2 < slot.end_time])
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
        text = "Pas à la fois à " + str(self.time1/60) + "h et à" + str(self.time2/60) + "h."
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
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
    type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    possible_start_times = ArrayField(models.PositiveSmallIntegerField())




    def enrich_model(self, ttmodel, week, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.train_progs.exists():
            fc = fc.filter(group__train_prog__in=self.train_progs.all())
        if self.group is not None:
            fc = fc.filter(group=self.group)
        possible_slots_ids = set(slot.id for slot in ttmodel.wdb.slots
                                 if slot.start_time in self.possible_start_times.values_list())

        for c in fc:
            for sl in ttmodel.wdb.slots.exclude(id__in=possible_slots_ids):
                if self.weight is not None:
                    ttmodel.obj += self.local_weight() * ponderation * ttmodel.TT[(sl, c)]
                else:
                    ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0,
                                           Constraint(constraint_type=ConstraintType.LIMITED_START_TIME_CHOICES,
                                                      courses=fc, slots=sl))

    def one_line_description(self):
        text = "Les "
        if self.type:
            text += str(self.type)
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
        for sl in self.possible_start_times.values_list():
            if sl % 60==0:
                text += str(sl//60) + 'h, '
            else:
                text += str(sl//60) + 'h' + str(sl % 60) + ', '
        return text


class LimitedRoomChoices(TTConstraint):
    """
    Limit the possible rooms for the cources
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
    type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    possible_rooms = models.ManyToManyField('base.Room',
                                            related_name="limited_rooms")

    def enrich_model(self, ttmodel, week, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.group is not None:
            fc = fc.filter(group=self.group)
        possible_rooms_ids = self.possible_rooms.values_list('id', flat=True)

        for c in fc:
            for sl in ttmodel.wdb.slots:
                for rg in ttmodel.wdb.room_groups.filter(types__in=[c.room_type]).exclude(id__in = possible_rooms_ids):
                    if self.weight is not None:
                        ttmodel.obj += self.local_weight() * ponderation * ttmodel.TTrooms[(sl, c, rg)]
                    else:
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c,rg)], '==', 0,
                                               Constraint(constraint_type=ConstraintType.LIMITED_ROOM_CHOICES,
                                                          courses=c, slots=sl, rooms=rg))

    def one_line_description(self):
        text = "Les "
        if self.type:
            text += str(self.type)
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










#
#   CustomConstraint
#


def get_constraint_list():
    """
    Return constraint class list contained in CUSTOM_CONSTRAINTS_PATH
    """
    try:
        module = importlib.import_module(settings.CUSTOM_CONSTRAINTS_PATH)
        classes = inspect.getmembers(module, inspect.isclass)

        constraints = []
        for class_name, _ in classes:
            fully_qualified_name = f'{module.__name__}.{class_name}'
            constraints.append((fully_qualified_name, fully_qualified_name))

        return constraints
    except ModuleNotFoundError:
        print(f"can't find the {settings.CUSTOM_CONSTRAINTS_PATH} module")


class CustomConstraint(TTConstraint):
    """
    Call a custom constraint implementation.
    """

    class_name = models.CharField(
                    max_length=200,
                    null=False,
                    blank=False)
    groups = models.ManyToManyField('base.Group', blank=True)
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    modules = models.ManyToManyField('base.Module', blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Delay class_name field choices loading
        self._meta.get_field('class_name').choices = lazy(get_constraint_list, list)()
        self.constraint = None

    def get_constraint(self, class_name):
        """
        Return class_method located in the targeted constraint class instance
        """
        if self.constraint is None:
            module_name, class_name = class_name.rsplit('.', 1)
            try:
                # Get class instance
                module = importlib.import_module(module_name)
                self.constraint = getattr(module, class_name)()
            except ModuleNotFoundError:
                print(f"can't find the <{module_name}> module")
            except:
                print(f"an error has occured while loading class <{class_name}>")

        return self.constraint

    def get_method(self, method_name):
        """
        Return the method reference by inspecting the constraint instance
        """
        method = None
        constraint = self.get_constraint(self.class_name)
        if constraint:
            method = getattr(constraint, method_name, None)
        return method

    def inject_method(func):
        """
        This decorator lookup for a method, in the class described by
        class_name attribute, with the same name as the decorated method.
        Once retrieve the method is then injected as a method keyword parameter.
        """
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            method = self.get_method(func.__name__)
            return func(self, *args, injected_method=method, **kwargs)

        return _wrapper

    @inject_method
    def enrich_model(self, ttmodel, week, ponderation=1, injected_method=None):
        """
        Call custom constraint method
        """
        args = {}

        if self.groups.count():
            args.update({'groups': list(self.groups.all())})


        if self.tutors.count():
            args.update({'tutors': list(self.tutors.all())})


        if self.modules.count():
            args.update({'modules': list(self.modules.all())})


        if self.train_progs.count():
            args.update({'train_progs': list(self.train_progs.all())})

        if injected_method:
            injected_method(ttmodel, ponderation, **args)

    @inject_method
    def one_line_description(self, injected_method=None):
        description = ''
        if injected_method:
            description = injected_method()
            if not description:
                description = self.class_name
        return description

    @inject_method
    def get_viewmodel(self, injected_method=None):
        view_model = super().get_viewmodel()
        details = view_model['details']
        if injected_method:
            details.update({'class': self.class_name})
            details.update(injected_method())
        else:
            details.update({'class': f'{self.class_name} class not found'})

        return view_model
