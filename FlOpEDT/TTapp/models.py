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
        if self.day == other.day and \
                (other.start_time <= self.start_time < other.end_time
                 or self.start_time <= other.start_time < self.end_time):
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
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None, 
                                   blank=True, 
                                   on_delete=models.CASCADE)    
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
        if self.train_prog:
            train_prog_value = f"{self.train_prog.name} ({self.train_prog.abbrev})" 
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
                'train_prog': train_prog_value,
                'week': week_value,
                'weight': self.weight,
                }
            }

    def one_line_description(self):
        # Return a human readable constraint name with its attributes
        raise NotImplementedError

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        return ['train_prog', 'department',]

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
            try:
                # Get class instance
                module_name, class_name = class_name.rsplit('.', 1)
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
    module = models.ForeignKey('base.Module',
                                   null=True,
                                   default=None, 
                                   blank=True,
                                   on_delete=models.CASCADE)
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="Course_type_limits")
    FULL_DAY = 'fd'
    HALF_DAY = 'hd'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (HALF_DAY, 'Half day'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)

    def get_courses_queryset(self, ttmodel, tutor=None):
        """
        Filter courses depending on constraints parameters
        """
        courses_qs = ttmodel.wdb.courses.filter(type=self.course_type)
        courses_filter = {}

        if tutor is not None:
            courses_filter['tutor'] = tutor

        if self.module is not None:
            courses_filter['module'] = self.module

        if self.train_prog is not None:
            courses_filter['group__train_prog'] = self.train_prog

        return courses_qs.filter(**courses_filter)

    def register_expression(self, ttmodel, period_by_day, ponderation, tutor=None):

        courses = set(self.get_courses_queryset(ttmodel, tutor))

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
                name = 'Max_%d_hours_of_%s_per_%s_%s_%s%g' % (self.max_hours,
                                                              self.course_type,
                                                              self.period,
                                                              day,
                                                              period if period is not None else '',
                                                              ttmodel.constraint_nb)
                ttmodel.add_constraint(expr, '<=', self.max_hours*60, name=name)

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
            else:
                self.register_expression(ttmodel, period_by_day, ponderation)
        except ValueError:
            self.register_expression(ttmodel, period_by_day, ponderation)

    def full_name(self):
        return "Limit Course Type Per Period"

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['module', 'tutors', 'type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        if self.course_type:
            type_value = self.course_type.name
        else:
            type_value = 'All'

        if self.module:
            module_value = self.module.name
        else:
            module_value = 'All'

        if self.tutors:
            tutor_value = ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            tutor_value = 'All'

        view_model['details'].update({
            'type': type_value,
            'tutor': tutor_value,
            'module': module_value, })

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_hours) + ' heures de ' + str(self.course_type)
        if self.module:
            text += " de " + self.module.name
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demi-journée'
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.train_prog:
            text += ' en ' + str(self.train_prog)

        return text


class ReasonableDays(TTConstraint):
    """
    Allow to limit long days (with the first and last slot of a day). For a
    given parameter,
    a None value builds the constraint for all possible values,
    e.g. promo = None => the constraint holds for all promos.
    """
    groups = models.ManyToManyField('base.Group',
                                    blank=True,
                                    related_name="reasonable_day_constraints")
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="reasonable_day_constraints")

    def get_courses_queryset(self, ttmodel, tutor=None, group=None):
        """
        Filter courses depending on constraints parameters
        """
        courses_qs = ttmodel.wdb.courses
        courses_filter = {}

        if tutor is not None:
            courses_filter['tutor'] = tutor

        if group is not None:
            courses_filter['group'] = group

        if self.train_prog is not None:
            courses_filter['group__train_prog'] = self.train_prog

        return courses_qs.filter(**courses_filter)


    def update_combinations(self, ttmodel, slot_boundaries, combinations, tutor=None, group=None):
        """
        Update courses combinations for slot boundaries with all courses 
        corresponding to the given filters (tutors, groups)
        """
        courses_query = self.get_courses_queryset(ttmodel, tutor=tutor, group=group)
        courses_set = set(courses_query)
        
        for first_slot, last_slot in slot_boundaries:
            while courses_set:
                c1 = courses_set.pop()
                for c2 in courses_set:
                    combinations.add(((first_slot, c1), (last_slot, c2),))


    def register_expression(self, ttmodel, ponderation, combinations):
        """
        Update model with expressions corresponding to 
        all courses combinations
        """
        for first, last in combinations:
            if self.weight is not None:
                conj_var = ttmodel.add_conjunct(ttmodel.TT[first], ttmodel.TT[last])
                ttmodel.obj += self.local_weight() * ponderation * conj_var
            else:
                ttmodel.add_constraint(ttmodel.TT[first] + ttmodel.TT[last], '<=', 1)


    def enrich_model(self, ttmodel, week, ponderation=1):
        # Using a set type ensure that all combinations are
        # unique throw tutor and group filters
        combinations = set()

        # Get two dicts with the first and last slot by day
        first_slots = set([slot for slot in ttmodel.wdb.slots if slot.start_time <= 9*60])
        last_slots = set([slot for slot in ttmodel.wdb.slots if slot.end_time > 18*60])
        slots = first_slots | last_slots

        
        slot_boundaries = {}
        for slot in slots:
            slot_boundaries.setdefault(slot.day, []).append(slot)
              
        # Create all combinations with slot boundaries for all courses
        # corresponding to the given filters (tutors, groups)
        try:
            if self.tutors.count():
                for tutor in self.tutors.all():
                    self.update_combinations(ttmodel, slot_boundaries.values(), combinations, tutor=tutor)
            elif self.groups.count():
                for group in self.groups.all():
                    self.update_combinations(ttmodel, slot_boundaries.values(), combinations, group=group)
            else:
                self.update_combinations(ttmodel, slot_boundaries.values(), combinations)
        except ValueError:
            self.update_combinations(ttmodel, slot_boundaries.values(), combinations)

        self.register_expression(ttmodel, ponderation, combinations)


    def one_line_description(self):
        text = "Des journées pas trop longues"
        if self.tutors.count():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.groups.count():
            text += ' avec les groupes ' + ', '.join([group for group in self.groups.all()])
        return text


    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['groups', 'tutors'])
        return attributes


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
        for day in days_filter(self.fixed_days.all(), week=week):
            for sc in sched_courses.filter(slot__jour=day):
                ttmodel.add_constraint(ttmodel.TT[(sc.slot, sc.course)], '==', 1)
            for sc in sched_courses.exclude(slot__day=day):
                for sl in ttmodel.wdb.slots.filter(day=day):
                    ttmodel.add_constraint(ttmodel.TT[(sl, sc.course)], '==', 0)

        if self.general:
            # nb_changements_I=dict(zip(ttmodel.wdb.instructors,[0 for i in ttmodel.wdb.instructors]))
            for sl in slots_filter(ttmodel.wdb.slots, week=week):
                for c in ttmodel.wdb.compatible_courses[sl]:
                    if not sched_courses.filter(Q(start_time__gte=sl.start_time,
                                                      start_time__lt=sl.end_time) |
                                                    Q(start_time__lte=sl.start_time,
                                                      start_time__gt=sl.start_time - F('course__type__duration')),
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
            if self.train_prog is not None:
                fc = fc.filter(group__train_prog=self.train_prog)
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
                                                   0)

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
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
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
            
        if self.train_prog:
            text += ' en ' + str(self.train_prog)

        return text
        

class MinNonPreferedSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots
    NB: You HAVE TO chose either tutor OR train_prog
    """
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutor'])
        return attributes                              

    # is not called when save() is
    def clean(self):
        if not self.tutor and not self.train_prog:
            raise ValidationError({
                'train_prog': ValidationError(_('Si pas de prof alors promo.',
                                                code='invalid')),
                'tutor': ValidationError(_('Si pas de promo alors prof.',
                                           code='invalid'))})

    def enrich_model(self, ttmodel, week, ponderation=1):
        if self.tutor is not None:
            filtered_courses = set(c for c in ttmodel.wdb.courses_for_tutor[self.tutor] if c.week == week)
        else:
            filtered_courses = ttmodel.wdb.courses \
                .filter(group__train_prog=self.train_prog, week=week)
            # On exclut les cours de sport!
            filtered_courses = \
                filtered_courses.exclude(module__abbrev='SC')
            filtered_courses = set(filtered_courses)
        basic_groups = ttmodel.wdb.basic_groups \
            .filter(train_prog=self.train_prog)
        for sl in ttmodel.wdb.slots:
            for c in filtered_courses & ttmodel.wdb.compatible_courses[sl]:
                if self.tutor is not None:
                    cost = (float(self.weight) / max_weight) \
                           * ponderation * ttmodel.TT[(sl, c)] \
                           * ttmodel.unp_slot_cost[c.tutor][sl]
                    #ttmodel.add_to_slot_cost(sl, cost)
                    ttmodel.add_to_inst_cost(c.tutor, cost)
                else:
                    for g in basic_groups:
                        if c.group in ttmodel.wdb.all_groups_of[g]:
                            cost = self.local_weight() \
                                   * ponderation * ttmodel.TT[(sl, c)] \
                                   * ttmodel.unp_slot_cost_course[c.type,
                                                                  self.train_prog][sl]
                            ttmodel.add_to_group_cost(g, cost)
                            #ttmodel.add_to_slot_cost(sl, cost)

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_prog:
            text += ' des groupes de ' + str(self.train_prog)
        return text


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
                                                   1)

    def one_line_description(self):
        text = "Pas à la fois à " + str(self.time1/60) + "h et à" + str(self.time2/60) + "h."
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        return text


class SimultaneousCourses(TTConstraint):
    """
    Force two courses to be simultaneous
    It modifies the core constraints that impides such a simultaneity
    """
    course1 = models.ForeignKey('base.Course', related_name='course1', on_delete=models.CASCADE)
    course2 = models.ForeignKey('base.Course', related_name='course2', on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['course1', 'course2'])
        return attributes

    def enrich_model(self, ttmodel, ponderation=1):
        same_tutor = (self.course1.tutor == self.course2.tutor)
        for sl in ttmodel.wdb.compatible_slots[self.course1] & ttmodel.wdb.compatible_slots[self.course2]:
            var1 = ttmodel.TT[(sl, self.course1)]
            var2 = ttmodel.TT[(sl, self.course2)]
            ttmodel.add_constraint(var1 - var2, '==', 0)
            # A compléter, l'idée est que si les cours ont le même prof, ou des
            # groupes qui se superposent, il faut veiller à supprimer les core
            # constraints qui empêchent que les cours soient simultanés...
            if same_tutor and self.course1.tutor in ttmodel.wdb.instructors:
                for sl2 in ttmodel.wdb.slots_intersecting[sl] - {sl}:
                    name_tutor_constr_sl2 = 'simul_slots' + str(self.course1.tutor) + '_' + str(sl) + '_' + str(sl2)
                    tutor_constr = ttmodel.get_constraint(name_tutor_constr_sl2)
                    print(tutor_constr)
                    if ttmodel.var_coeff(var1, tutor_constr) == 1:
                        ttmodel.change_var_coeff(var1, tutor_constr, 0)
            for bg in ttmodel.wdb.basic_groups:
                bg_groups = ttmodel.wdb.all_groups_of[bg]
                if self.course1.group in bg_groups and self.course2.group in bg_groups:
                    for sl2 in ttmodel.wdb.slots_intersecting[sl] - {sl}:
                        name_group_constr_sl2 = 'simul_slots' + bg.full_name() + '_' + str(sl) + '_' + str(sl2)
                        group_constr = ttmodel.get_constraint(name_group_constr_sl2)
                        if ttmodel.var_coeff(var1, group_constr) == 1:
                            ttmodel.change_var_coeff(var1, group_constr, 0)

    def one_line_description(self):
        return "Les cours " + str(self.course1) + " et " + str(self.course2) + " doivent être simultanés !"


class LimitedStartTimeChoices(TTConstraint):
    """
    Limit the possible slots for the courses
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




    def enrich_model(self, ttmodel, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.train_prog is not None:
            fc = fc.filter(group__train_prog=self.train_prog)
        if self.group is not None:
            fc = fc.filter(group=self.group)
        possible_slots_ids = set(slot.id for slot in ttmodel.wdb.slots
                                 if slot.start_time in self.possible_start_times.values_list())

        for c in fc:
            for sl in ttmodel.wdb.slots.exclude(id__in=possible_slots_ids):
                if self.weight is not None:
                    ttmodel.obj += self.local_weight() * ponderation * ttmodel.TT[(sl, c)]
                else:
                    ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)

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
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
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
    possible_rooms = models.ManyToManyField('base.RoomGroup',
                                            related_name="limited_rooms")

    def enrich_model(self, ttmodel, ponderation=1.):
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
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c,rg)], '==', 0)

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
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'en salle "
        for sl in self.possible_rooms.values_list():
            text += str(sl) + ', '
        return text
