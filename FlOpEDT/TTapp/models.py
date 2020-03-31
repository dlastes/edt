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
import sys
from functools import wraps

from django.conf import settings
from django.utils.functional import lazy

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

from django.db import models

from django.db.models import Q, F

# from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _

# from caching.base import CachingManager, CachingMixin

from base.models import Time, Department, Module, Group, Day

from people.models import Tutor

from TTapp.helpers.minhalfdays import MinHalfDaysHelperGroup, MinHalfDaysHelperModule, MinHalfDaysHelperTutor

from TTapp.constraint_type import ConstraintType

max_weight = 8

slot_pause = 30

PM_start = 12*60

basic_slot_duration = 90

days_list = [c[0] for c in Day.CHOICES]
days_index = {}
for c in Day.CHOICES:
    days_index[c[0]] = days_list.index(c[0])


class Slot(object):
    def __init__(self, day, start_time, course_type=None):
        self.course_type = course_type
        self.day = day
        self.start_time = start_time
        self.duration = basic_slot_duration
        if self.course_type is not None:
            self.duration = self.course_type.duration
        self.end_time = self.start_time + self.duration
        if self.start_time >= PM_start:
            self.apm = Time.PM
        else:
            self.apm = Time.AM


    def is_simultaneous_to(self, other):
        if self.day == other.day and self.start_time < other.end_time and other.start_time < self.end_time:
            return True
        else:
            return False

    def is_after(self, other):
        if self.day.week > other.day.week \
                or self.day.week == other.day.week and days_index[self.day.day] > days_index[other.day.day] \
                or self.day == other.day and self.start_time >= other.end_time:
            return True
        else:
            return False

    def is_successor_of(self, other):
        if self.day == other.day and other.end_time <= self.start_time <= other.end_time + slot_pause:
            return True
        else:
            return False

    def __lt__(self, other):
        return other.is_after(self) and not self.is_after(other)

    def __str__(self):
        hours = self.start_time//60
        minuts = self.start_time % 60
        if minuts == 0:
            minuts = ''
        return str(self.course_type) + '_' + str(self.day) + '_' + str(hours) + 'h' + str(minuts)

    def __repr__(self):
        return str(self)

    def get_day(self):
        return self.day
        
def slots_filter(slot_set, day=None, apm=None, course_type=None, start_time=None, week_day=None,
                 simultaneous_to=None, week=None, is_after=None, starts_after=None, starts_before=None, ends_before=None):
    slots = slot_set
    if week is not None:
        slots = set(sl for sl in slots if sl.day.week == week)
    if day is not None:
        slots = set(sl for sl in slots if sl.day == day)
    if week_day is not None:
        slots = set(sl for sl in slots if sl.day.day == week_day)
    if course_type is not None:
        slots = set(sl for sl in slots if sl.course_type == course_type)
    if apm is not None:
        slots = set(sl for sl in slots if sl.apm == apm)
    if simultaneous_to is not None:
        slots = set(sl for sl in slots if sl.is_simultaneous_to(simultaneous_to))
    if is_after is not None:
        slots = set(sl for sl in slots if sl.is_after(is_after))
    if starts_after is not None:
        slots = set(sl for sl in slots if sl.start_time >= starts_after)
    if starts_before is not None:
        slots = set(sl for sl in slots if sl.start_time <= starts_before)
    if ends_before is not None:
        slots = set(sl for sl in slots if sl.end_time <= ends_before)
    if start_time is not None:
        slots = set(sl for sl in slots if sl.start_time == start_time)
    return slots


def days_filter(days_set, index=None, index_in=None, week=None, week_in=None, day=None):
    days = days_set
    if week is not None:
        days = set(d for d in days if d.week == week)
    if week_in is not None:
        days = set(d for d in days if d.week in week_in)
    if index is not None:
        days = set(d for d in days if days_index[d.day] == index)
    if index_in is not None:
        days = set(d for d in days if days_index[d.day] in index_in)
    if day is not None:
        days = set(d for d in days if d.day == day)
    return days


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
                slots = ttmodel.wdb.slots_by_day[day]
            else:
                slots = ttmodel.wdb.slots_by_half_day[(day, period)]

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
                                       constraint_type=ConstraintType.MAX_HOURS, modules=self.course_type, days=day)

    def enrich_model(self, ttmodel, week, ponderation=1.):

        if self.period == self.FULL_DAY:
            periods = [None]
        else:
            periods = [Time.AM, Time.PM]

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
                                                   0, constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL, courses=fc, slots=slot)

        # else:
        #     fc = ttmodel.wdb.courses
        #     if self.tutor is not None:
        #         fc = fc.filter(tutor=self.tutor)
        #     if self.type is not None:
        #         fc = fc.filter(type=self.type)
        #     if self.train_prog is not None:
        #         fc = fc.filter(group__train_prog=self.train_prog)
        #     if self.group:
        #         fc = fc.filter(group=self.group)
        #     if self.module:
        #         fc = fc.filter(module=self.module)
        #     for c in fc:
        #         sched_c = ttmodel.wdb \
        #             .sched_courses \
        #             .get(course=c,
        #                  work_copy=self.work_copy)
        #         chosen_slot = sched_c.creneau
        #         chosen_roomgroup = sched_c.room
        #         if self.weight is not None:
        #             ttmodel.obj -= self.local_weight() \
        #                            * ponderation * ttmodel.TT[(chosen_slot, c)]
        #
        #         else:
        #             ttmodel.add_constraint(ttmodel.TT[(chosen_slot, c)],
        #                                    '==',
        #                                    1)
        #             if c.room_type in chosen_roomgroup.types.all():
        #                 ttmodel.add_constraint(
        #                     ttmodel.TTrooms[(chosen_slot, c, chosen_roomgroup)],
        #                     '==',
        #                     1)

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


class MinHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    You have to chose EITHER tutor OR group OR module
    Optional for tutors : if 2 courses only, possibility to join it
    """
    groups = models.ManyToManyField('base.Group', blank=True)
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    modules = models.ManyToManyField('base.Module', blank=True)

    join2courses = models.BooleanField(
        verbose_name='If a tutor has 2 or 4 courses only, join it?',
        default=False)


    def enrich_model(self, ttmodel, week, ponderation=1):

        if self.tutors.exists():
            helper = MinHalfDaysHelperTutor(ttmodel, self, week, ponderation)
            for tutor in self.tutors.all():
                if tutor in ttmodel.wdb.instructors:
                    helper.enrich_model(tutor=tutor)

        elif self.modules.exists():
            helper = MinHalfDaysHelperModule(ttmodel, self, week, ponderation)
            for module in self.modules.all():
                helper.enrich_model(module=module)

        elif self.groups.exists():
            helper = MinHalfDaysHelperGroup(ttmodel, self, week, ponderation)
            for group in self.groups.all():
                helper.enrich_model(group=group)

        else:
            print("MinHalfDays must have at least one tutor or one group or one module --> Ignored")
            return


    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        if self.groups.exists():
            details.update({'groups': ', '.join([group.name for group in self.groups.all()])})

        if self.modules.exists():
            details.update({'modules': ', '.join([module.name for module in self.modules.all()])})

        return view_model


    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.tutors.exists():
            text += ' de : ' + ', '.join([tutor.username for tutor in self.tutors.all()])

        if self.groups.exists():
            text += ' du(des) groupe(s) : ' + ', '.join([group.name for group in self.groups.all()])

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
                                    related_name='min_non_prefered_slots_constraints')

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutors'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
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

    def enrich_model(self, ttmodel, week, ponderation=1):
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