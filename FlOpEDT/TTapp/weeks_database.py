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

from base.models import Group, \
    Room, RoomSort, RoomType, RoomPreference, \
    Course, ScheduledCourse, UserPreference, CoursePreference, \
    Department, Module, TrainingProgramme, CourseType, \
    Dependency, TutorCost, GroupFreeHalfDay, GroupCost, Holiday, TrainingHalfDay, \
    CourseStartTimeConstraint, TimeGeneralSettings, ModulePossibleTutors, CoursePossibleTutors

from base.timing import Time, Day

import base.queries as queries

from people.models import Tutor


from TTapp.slots import Slot, CourseSlot, slots_filter, days_filter

from django.db.models import Q, Max, F

import logging

from base.models import ModuleTutorRepartition


logger = logging.getLogger(__name__)
pattern = r".+: (.|\s)+ (=|>=|<=) \d*"
GUROBI = 'GUROBI'
GUROBI_NAME = 'GUROBI_CMD'


class WeeksDatabase(object):
    def __init__(self, department, weeks, year, train_prog, slots_step=None):
        self.train_prog = train_prog
        self.department = department
        self.weeks = weeks
        self.year = year
        self.slots_step = slots_step
        if settings.VISIO_MODE:
            self.visio_room, visio_room_created = Room.objects.get_or_create(name='Visio')
        self.possible_apms=set()
        self.days, self.day_after, self.holidays, self.training_half_days = self.days_init()
        self.courses_slots, self.availability_slots = self.slots_init()
        self.course_types, self.courses, self.courses_by_week, \
        self.sched_courses, self.fixed_courses, self.fixed_courses_for_avail_slot, \
        self.other_departments_courses, self.other_departments_sched_courses, \
        self.other_departments_sched_courses_for_avail_slot, \
        self.courses_availabilities, self.modules, self.dependencies = self.courses_init()
        self.room_types, self.rooms, self.basic_rooms, self.room_prefs, self.rooms_for_type, \
        self.room_course_compat, self.course_rg_compat, self.fixed_courses_for_room, \
        self.other_departments_sched_courses_for_room = self.rooms_init()
        self.compatible_slots, self.compatible_courses = self.compatibilities_init()
        self.groups, self.basic_groups, self.all_groups_of, self.basic_groups_of, self.courses_for_group, \
        self.courses_for_basic_group = self.groups_init()
        self.instructors, self.courses_for_tutor, self.courses_for_supp_tutor, self.availabilities, \
        self.fixed_courses_for_tutor, \
        self.other_departments_courses_for_tutor, self.other_departments_scheduled_courses_for_supp_tutor, \
        self.other_departments_scheduled_courses_for_tutor = self.users_init()
        self.possible_tutors, self.possible_modules, self.possible_courses = self.possible_courses_tutor_init()

    def days_init(self):
        holidays = Holiday.objects.filter(week__in=self.weeks, year=self.year)

        training_half_days = TrainingHalfDay.objects.filter(
            week__in=self.weeks,
            year=self.year,
            train_prog__in=self.train_prog)

        days = [Day(week=week, day=day)
                for week in self.weeks
                for day in TimeGeneralSettings.objects.get(department=self.department).days]

        for hd in holidays:
            for day in days:
                if day.day == hd.day and day.week == hd.week:
                    days.remove(day)

        day_after = {}
        for i, day in enumerate(days):
            try:
                day_after[day] = days[i + 1]
            except IndexError:
                day_after[day] = None
        days = set(days)

        return days, day_after, holidays, training_half_days

    def slots_init(self):
        # SLOTS
        print('Slot tools definition', end=', ')
        tgs = TimeGeneralSettings.objects.get(department=self.department)
        courses_slots = set()
        for cc in CourseStartTimeConstraint.objects.filter(Q(course_type__department=self.department)
                                                           | Q(course_type=None)):
            if self.slots_step is None:
                courses_slots |= set(CourseSlot(d, start_time, cc.course_type)
                             for d in self.days
                             for start_time in cc.allowed_start_times)
            else:
                courses_slots |= set(CourseSlot(d, start_time, cc.course_type)
                                     for d in self.days
                                     for start_time in cc.allowed_start_times if start_time % self.slots_step == 0)

        for slot in courses_slots:
            self.possible_apms.add(slot.apm)

        dayly_availability_slots= set()
        for ct in self.department.coursetype_set.all():
            for cst in ct.coursestarttimeconstraint_set.all():
                dayly_availability_slots |= set(cst.allowed_start_times)
        dayly_availability_slots.add(tgs.day_finish_time)
        dayly_availability_slots = list(dayly_availability_slots)
        dayly_availability_slots.sort()
        start_times = dayly_availability_slots[:-1]
        end_times = dayly_availability_slots[1:]
        for i in range(len(end_times)):
            if tgs.lunch_break_start_time < end_times[i] <= tgs.lunch_break_finish_time:
                end_times[i] = tgs.lunch_break_start_time

        availability_slots = {Slot(day=day,
                                   start_time=start_times[i],
                                   end_time=end_times[i])
                              for day in self.days
                              for i in range(len(start_times))}
        print('Ok' + f' : {len(courses_slots)} courses_slots and {len(availability_slots)} availability_slots created!')

        return courses_slots, availability_slots

    def courses_init(self):
        # COURSES
        course_types = CourseType.objects.filter(department=self.department)

        courses = Course.objects.filter(week__in=self.weeks, year=self.year, module__train_prog__in=self.train_prog)\
            .select_related('module')

        courses_by_week = {week: set(courses.filter(week=week)) for week in self.weeks}

        sched_courses = ScheduledCourse \
            .objects \
            .filter(course__week__in=self.weeks,
                    course__year=self.year,
                    course__module__train_prog__in=self.train_prog,
                    work_copy=0)

        fixed_courses = ScheduledCourse.objects \
            .filter(course__module__train_prog__department=self.department,
                    course__week__in=self.weeks,
                    course__year=self.year,
                    work_copy=0) \
            .exclude(course__module__train_prog__in=self.train_prog)

        fixed_courses_for_avail_slot = {}
        for sl in self.availability_slots:
            fixed_courses_for_avail_slot[sl] = set(fc for fc in fixed_courses
                                                   if fc.start_time < sl.end_time
                                                   and sl.start_time < fc.end_time
                                                   and fc.day == sl.day.day
                                                   and fc.course.week == sl.day.week)

        other_departments_courses = Course.objects.filter(
            week__in=self.weeks, year=self.year) \
            .exclude(type__department=self.department)

        other_departments_sched_courses = ScheduledCourse \
            .objects \
            .filter(course__in=other_departments_courses,
                    work_copy=0)

        other_departments_sched_courses_for_avail_slot = {}
        for sl in self.availability_slots:
            other_departments_sched_courses_for_avail_slot[sl] = \
                set(fc for fc in other_departments_sched_courses
                    if fc.start_time < sl.end_time and sl.start_time < fc.end_time
                    and fc.day == sl.day.day and fc.course.week == sl.day.week)

        courses_availabilities = CoursePreference.objects \
            .filter(Q(week__in=self.weeks, year=self.year) | Q(week=None),
                    train_prog__department=self.department)

        modules = Module.objects \
            .filter(id__in=courses.values_list('module_id').distinct())

        dependencies = Dependency.objects.filter(
            course1__week__in=self.weeks,
            course1__year=self.year,
            course2__week__in=self.weeks,
            course1__module__train_prog__in=self.train_prog)

        return course_types, courses, courses_by_week, sched_courses, fixed_courses, \
               fixed_courses_for_avail_slot, \
               other_departments_courses, other_departments_sched_courses, \
               other_departments_sched_courses_for_avail_slot, \
               courses_availabilities, modules, dependencies

    def rooms_init(self):
        # ROOMS
        room_types = RoomType.objects.filter(department=self.department)
        basic_rooms = queries.get_rooms(self.department.abbrev, basic=True).distinct()
        room_prefs = RoomSort.objects.filter(for_type__department=self.department)
        rooms_for_type = {t: t.members.all() for t in room_types}

        rooms = set(Room.objects.filter(departments=self.department).distinct())
        for r in basic_rooms:
            rooms |= r.and_overrooms()

        # for each Room, first build the list of courses that may use it
        room_course_compat = {}
        for r in basic_rooms:
            # print "compat for ", r
            room_course_compat[r] = []
            for rg in r.and_overrooms():
                room_course_compat[r].extend(
                    [(c, rg) for c in
                     self.courses.filter(room_type__in=rg.types.all())])

        course_rg_compat = {}
        for c in self.courses:
            course_rg_compat[c] = set(c.room_type.members.all())
            if settings.VISIO_MODE:
                course_rg_compat[c] |= {self.visio_room}

        fixed_courses_for_room = {}
        for r in basic_rooms:
            fixed_courses_for_room[r] = set()
            for rg in r.and_overrooms():
                fixed_courses_for_room[r] |= set(self.fixed_courses.filter(room=rg))

        other_departments_sched_courses_for_room = {}
        for r in basic_rooms:
            other_departments_sched_courses_for_room[r] = set()
            for rg in r.and_overrooms():
                other_departments_sched_courses_for_room[r] |= set(self.other_departments_sched_courses.filter(room=rg))

        return room_types, rooms, basic_rooms, room_prefs, rooms_for_type, room_course_compat, course_rg_compat, \
               fixed_courses_for_room, other_departments_sched_courses_for_room

    def compatibilities_init(self):
        # COMPATIBILITY
        # Slots and courses are compatible if they have the same type
        # OR if slot type is None and they have the same duration
        if not settings.COSMO_MODE:
            compatible_slots = {}
            for c in self.courses:
                compatible_slots[c] = set(slot for slot in self.courses_slots
                                          if slot.day.week == c.week and
                                          (slot.course_type == c.type
                                           or (slot.course_type is None and c.type.duration == slot.duration)))

            compatible_courses = {}
            for sl in self.courses_slots:
                if sl.course_type is None:
                    compatible_courses[sl] = set(course for course in self.courses
                                                 if course.type.duration == sl.duration
                                                 and sl.day.week == course.week)
                else:
                    compatible_courses[sl] = set(course for course in self.courses
                                                 if course.type == sl.course_type
                                                 and sl.day.week == course.week)
        else:
            compatible_courses = {sl: set() for sl in self.courses_slots}
            compatible_slots = {c: set() for c in self.courses}

            for c in self.courses:
                sc = self.sched_courses.get(course=c)
                if not c.suspens:
                    slots = {slot for slot in slots_filter(self.courses_slots, week=sc.course.week,
                                                           start_time=sc.start_time, course_type=sc.course.type)
                             if slot.day.day == sc.day}
                    if len(slots) == 1:
                        sl = slots.pop()
                    else:
                        raise TypeError("Many possible slots...?")
                    compatible_courses[sl].add(c)
                    compatible_slots[c] = {sl}
                else:
                    slots = set([slot for slot in slots_filter(self.courses_slots, week=sc.course.week,
                                                               course_type=sc.course.type)
                                 if 9 * 60 <= slot.start_time <= 18 * 60
                                 and slot.day.day not in [Day.SUNDAY, Day.SATURDAY]])
                    compatible_slots[c] = slots
                    for sl in slots:
                        compatible_courses[sl].add(c)
        return compatible_slots, compatible_courses

    def groups_init(self):
        # GROUPS
        groups = Group.objects.filter(train_prog__in=self.train_prog)

        basic_groups = groups.filter(basic=True)
        #  ,
        # id__in=self.courses.values_list('groupe_id').distinct())

        all_groups_of = {}
        for g in basic_groups:
            all_groups_of[g] = [g] + list(g.ancestor_groups())

        basic_groups_of = {}
        for g in groups:
            basic_groups_of = []
            for bg in basic_groups:
                if g in all_groups_of[bg]:
                    basic_groups_of.append(bg)

        courses_for_group = {}
        for g in groups:
            courses_for_group[g] = set(self.courses.filter(groups=g))

        courses_for_basic_group = {}
        for bg in basic_groups:
            courses_for_basic_group[bg] = set(self.courses.filter(groups__in=all_groups_of[bg]))

        return groups, basic_groups, all_groups_of, basic_groups_of, courses_for_group, courses_for_basic_group

    def users_init(self):
        # USERS

        instructors = set()
        for tutor in Tutor.objects.filter(id__in=self.courses.values_list('tutor_id')):
            instructors.add(tutor)
        for mpt in ModulePossibleTutors.objects.filter(module__in=self.modules):
            for tutor in mpt.possible_tutors.all():
                instructors.add(tutor)
        for cpt in CoursePossibleTutors.objects.filter(course__in=self.courses):
            for tutor in cpt.possible_tutors.all():
                instructors.add(tutor)
        for mtr in ModuleTutorRepartition.objects.filter(module__in=self.modules,
                                                         week__in=self.weeks,
                                                         year=self.year):
            instructors.add(mtr.tutor)
        try:
            no_tut = Tutor.objects.get(username='---')
            instructors.add(no_tut)
        except:
            pass
        courses_for_tutor = {}
        for i in instructors:
            courses_for_tutor[i] = set(self.courses.filter(tutor=i))

        courses_for_supp_tutor = {}
        for i in instructors:
            courses_for_supp_tutor[i] = set(i.courses_as_supp.filter(id__in=self.courses))

        availabilities = {}
        for i in instructors:
            availabilities[i] = {}
            for week in self.weeks:
                availabilities[i][week] = set(UserPreference.objects.filter(week=week, user=i, year=self.year))
                if not availabilities[i][week]:
                    availabilities[i][week] = set(UserPreference.objects.filter(week=None, user=i))

        fixed_courses_for_tutor = {}
        for i in instructors:
            fixed_courses_for_tutor[i] = set(self.fixed_courses.filter(tutor=i))

        other_departments_courses_for_tutor = {}
        for i in instructors:
            other_departments_courses_for_tutor[i] = set(self.other_departments_courses.filter(tutor=i))

        other_departments_scheduled_courses_for_supp_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_supp_tutor[i] = set(self.other_departments_sched_courses
                                                              .filter(course__supp_tutor=i))

        other_departments_scheduled_courses_for_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_tutor[i] = set(self.other_departments_sched_courses
                                                                   .filter(course__tutor=i))

        return instructors, courses_for_tutor, courses_for_supp_tutor, availabilities, \
               fixed_courses_for_tutor, other_departments_courses_for_tutor, \
               other_departments_scheduled_courses_for_supp_tutor, \
               other_departments_scheduled_courses_for_tutor

    def possible_courses_tutor_init(self):
        possible_tutors = {}
        try:
            no_tut = Tutor.objects.get(username='---')
        except:
            no_tut = None
        for m in self.modules:
            if ModulePossibleTutors.objects.filter(module=m).exists():
                possible_tutors[m] = set(ModulePossibleTutors.objects.get(module=m).possible_tutors.all())
            else:
                possible_tutors[m] = self.instructors
        for c in self.courses:
            if c.tutor is not None:
                possible_tutors[c] = {c.tutor}
            elif CoursePossibleTutors.objects.filter(course=c).exists():
                possible_tutors[c] = set(CoursePossibleTutors.objects.get(course=c).possible_tutors.all())
            elif ModuleTutorRepartition.objects.filter(course_type=c.type, module=c.module,
                                                       year=c.year, week=c.week).exists():
                possible_tutors[c] = set(mtr.tutor for mtr in
                                         ModuleTutorRepartition.objects.filter(course_type=c.type, module=c.module,
                                                                               year=c.year, week=c.week))
                if no_tut is not None:
                    possible_tutors[c].add(no_tut)
            else:
                possible_tutors[c] = possible_tutors[c.module]

        possible_modules = {}
        for i in self.instructors:
            possible_modules[i] = set(m for m in self.modules
                                      if i in possible_tutors[m])

        possible_courses = {}
        for i in self.instructors:
            possible_courses[i] = set(c for c in self.courses if i in possible_tutors[c])

        return possible_tutors, possible_modules, possible_courses
