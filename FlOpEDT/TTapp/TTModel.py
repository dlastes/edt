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

from pulp import GUROBI_CMD, PULP_CBC_CMD
import pulp.solvers as pulp_solvers
#from pulp.solvers import GUROBI_CMD as GUROBI

from FlOpEDT.settings.base import COSMO_MODE

from base.models import Group, Day, Time, \
    Room, RoomGroup, RoomSort, RoomType, RoomPreference, \
    Course, ScheduledCourse, UserPreference, CoursePreference, \
    Department, Module, TrainingProgramme, CourseType, \
    Dependency, TutorCost, GroupFreeHalfDay, GroupCost, Holiday, TrainingHalfDay, \
    CourseStartTimeConstraint, TimeGeneralSettings, ModulePossibleTutors, CoursePossibleTutors

from people.models import Tutor

from base.weeks import current_year

from TTapp.models import MinNonPreferedSlot, max_weight, Stabilize, TTConstraint, \
    Slot, slot_pause, basic_slot_duration, slots_filter, days_filter

from MyFlOp.MyTTUtils import reassign_rooms

import signal

from django.db import close_old_connections
from django.db.models import Q, Max, F
from django.conf import settings

import datetime

import logging

logger = logging.getLogger(__name__)
GUROBI_NAME = 'GUROBI_CMD'

class WeekDB(object):
    def __init__(self, department, weeks, year, train_prog):
        self.train_prog = train_prog
        self.department = department
        self.weeks = weeks
        self.year = year
        self.days, self.day_after, self.holidays, self.training_half_days = self.days_init()
        self.slots, self.slots_by_day, self.slots_intersecting, self.slots_by_half_day, self.slots_by_week \
            = self.slots_init()
        self.course_types, self.courses, self.courses_by_week, \
            self.sched_courses, self.fixed_courses, self.fixed_courses_for_slot, \
            self.other_departments_courses, self.other_departments_sched_courses, \
            self.other_departments_sched_courses_for_slot, \
            self.courses_availabilities, self.modules, self.dependencies = self.courses_init()
        self.room_types, self.room_groups, self.rooms, self.room_prefs, self.room_groups_for_type,\
            self.room_course_compat, self.course_rg_compat, self.fixed_courses_for_room, \
            self.other_departments_sched_courses_for_room = self.rooms_init()
        self.compatible_slots, self.compatible_courses = self.compatibilities_init()
        self.groups, self.basic_groups, self.all_groups_of, self.basic_groups_of, self.courses_for_group, \
            self.courses_for_basic_group = self.groups_init()
        self.instructors, self.courses_for_tutor, self.courses_for_supp_tutor, self.availabilities,\
            self.fixed_courses_for_tutor, \
            self.other_departments_courses_for_tutor, self.other_departments_courses_for_supp_tutor, \
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
                day_after[day] = days[i+1]
            except IndexError:
                day_after[day] = None
        days = set(days)

        return days, day_after, holidays, training_half_days

    def slots_init(self):
        # SLOTS
        print('Slot tools definition', end=', ')
        slots = set()
        for cc in CourseStartTimeConstraint.objects.filter(Q(course_type__department=self.department)
                                                           | Q(course_type=None)):
            slots |= set(Slot(d, start_time, cc.course_type)
                         for d in self.days
                         for start_time in cc.allowed_start_times)

        slots_by_day = {}
        for d in self.days:
            slots_by_day[d] = slots_filter(slots, day=d)

        slots_intersecting = {}
        for sl in slots:
            slots_intersecting[sl] = slots_filter(slots, simultaneous_to=sl)

        slots_by_half_day = {}
        for d in self.days:
            for apm in [Time.AM, Time.PM]:
                slots_by_half_day[(d, apm)] = slots_filter(slots, day=d, apm=apm)
        print('Ok')

        slots_by_week = {}
        for week in self.weeks:
            slots_by_week[week] = slots_filter(slots, week=week)

        return slots, slots_by_day, slots_intersecting, slots_by_half_day, slots_by_week

    def courses_init(self):
        # COURSES
        course_types = CourseType.objects.filter(department=self.department)

        courses = Course.objects.filter(
            week__in=self.weeks, year=self.year,
            group__train_prog__in=self.train_prog)

        courses_by_week = {week: set(courses.filter(week=week)) for week in self.weeks}

        sched_courses = ScheduledCourse \
            .objects \
            .filter(course__week__in=self.weeks,
                    course__year=self.year,
                    course__group__train_prog__in=self.train_prog,
                    work_copy=0)

        fixed_courses = ScheduledCourse.objects \
            .filter(course__group__train_prog__department=self.department,
                    course__week__in=self.weeks,
                    course__year=self.year,
                    work_copy=0) \
            .exclude(course__group__train_prog__in=self.train_prog)

        fixed_courses_for_slot = {}
        for sl in self.slots:
            fixed_courses_for_slot[sl] = set(fc for fc in fixed_courses
                                             if fc.start_time < sl.end_time
                                                and sl.start_time < fc.end_time()
                                                and fc.day == sl.day.day
                                                and fc.course.week == sl.day.week)

        other_departments_courses = Course.objects.filter(
            week__in=self.weeks, year=self.year)\
            .exclude(type__department=self.department)

        other_departments_sched_courses = ScheduledCourse \
            .objects \
            .filter(course__in=other_departments_courses,
                    work_copy=0)

        other_departments_sched_courses_for_slot = {}
        for sl in self.slots:
            other_departments_sched_courses_for_slot[sl] = set(fc for fc in other_departments_sched_courses
                                             if fc.start_time < sl.end_time and sl.start_time < fc.end_time()
                                                               and fc.day == sl.day)

        courses_availabilities = CoursePreference.objects \
            .filter(Q(week__in=self.weeks, year=self.year) | Q(week=None),
                    train_prog__department=self.department)

        modules = Module.objects \
            .filter(id__in=courses.values_list('module_id').distinct())

        dependencies = Dependency.objects.filter(
            course1__week__in=self.weeks,
            course1__year=self.year,
            course2__week__in=self.weeks,
            course1__group__train_prog__in=self.train_prog)

        return course_types, courses, courses_by_week, sched_courses, fixed_courses, fixed_courses_for_slot,\
            other_departments_courses, other_departments_sched_courses, other_departments_sched_courses_for_slot,\
            courses_availabilities, modules, dependencies

    def rooms_init(self):
        # ROOMS
        room_types = RoomType.objects.filter(department=self.department)
        room_groups = RoomGroup.objects.filter(types__department=self.department).distinct()
        rooms = Room.objects.filter(subroom_of__types__department=self.department).distinct()
        room_prefs = RoomSort.objects.filter(for_type__department=self.department)
        room_groups_for_type = {t: t.members.all() for t in room_types}
        # for each Room, first build the list of courses that may use it
        room_course_compat = {}
        for r in rooms:
            # print "compat for ", r
            room_course_compat[r] = []
            for rg in r.subroom_of.all():
                room_course_compat[r].extend(
                    [(c, rg) for c in
                     self.courses.filter(room_type__in=rg.types.all())])

        course_rg_compat = {}
        for c in self.courses:
            course_rg_compat[c] = c.room_type.members.all()

        fixed_courses_for_room = {}
        for r in rooms:
            fixed_courses_for_room[r] = set()
            for rg in r.subroom_of.all():
                fixed_courses_for_room[r] |= set(self.fixed_courses.filter(room=rg))

        other_departments_sched_courses_for_room = {}
        for r in rooms:
            other_departments_sched_courses_for_room[r] = set()
            for rg in r.subroom_of.all():
                other_departments_sched_courses_for_room[r] |= set(self.other_departments_sched_courses.filter(room=rg))
        return room_types, room_groups, rooms, room_prefs, room_groups_for_type, room_course_compat, course_rg_compat,\
            fixed_courses_for_room, other_departments_sched_courses_for_room

    def compatibilities_init(self):
        # COMPATIBILITY
        # Slots and courses are compatible if they have the same type
        # OR if slot type is None and they have the same duration
        if not COSMO_MODE:
            compatible_slots = {}
            for c in self.courses:
                compatible_slots[c] = set(slot for slot in self.slots
                                          if slot.day.week == c.week and
                                          (slot.course_type == c.type
                                           or (slot.course_type is None and c.type.duration == slot.duration)))

            compatible_courses = {}
            for sl in self.slots:
                if sl.course_type is None:
                    compatible_courses[sl] = set(course for course in self.courses
                                                 if course.type.duration == sl.duration
                                                 and sl.day.week == course.week)
                else:
                    compatible_courses[sl] = set(course for course in self.courses
                                                 if course.type == sl.course_type
                                                 and sl.day.week == course.week)
        else:
            compatible_courses = {sl: set() for sl in self.slots}
            compatible_slots = {c: set() for c in self.courses}

            for c in self.courses:
                sc = self.sched_courses.get(course=c)
                if not c.suspens:
                    slots = {slot for slot in slots_filter(self.slots, week=sc.course.week,
                                                           start_time=sc.start_time, course_type=sc.course.type)
                             if slot.day.day == sc.day}
                    if len(slots) == 1:
                        sl = slots.pop()
                    else:
                        raise TypeError("Many possible slots...?")
                    compatible_courses[sl].add(c)
                    compatible_slots[c] = {sl}
                else:
                    slots = set([slot for slot in slots_filter(self.slots, week=sc.course.week,
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
            courses_for_group[g] = set(self.courses.filter(group=g))

        courses_for_basic_group = {}
        for bg in basic_groups:
            courses_for_basic_group[bg] = set(self.courses.filter(group__in=all_groups_of[bg]))

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
            fixed_courses_for_tutor[i] = set(self.fixed_courses.filter(course__tutor=i))

        other_departments_courses_for_tutor = {}
        for i in instructors:
            other_departments_courses_for_tutor[i] = set(self.other_departments_courses.filter(tutor=i))

        other_departments_courses_for_supp_tutor = {}
        for i in instructors:
            other_departments_courses_for_supp_tutor[i] = set(self.other_departments_sched_courses
                                                                   .filter(course__supp_tutor=i))

        other_departments_scheduled_courses_for_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_tutor[i] = set(self.other_departments_sched_courses
                                                                   .filter(course__tutor=i))

        return instructors, courses_for_tutor, courses_for_supp_tutor, availabilities, \
            fixed_courses_for_tutor, other_departments_courses_for_tutor, other_departments_courses_for_supp_tutor, \
            other_departments_scheduled_courses_for_tutor

    def possible_courses_tutor_init(self):
        possible_tutors = {}
        for m in self.modules:
            if ModulePossibleTutors.objects.filter(module=m).exists():
                possible_tutors[m] = set(ModulePossibleTutors.objects.get(module=m).possible_tutors.all())
            else:
                possible_tutors[m] = self.instructors
        for c in self.courses:
            if c.tutor is not None:
                possible_tutors[c] = {c.tutor}
            elif CoursePossibleTutors.objects.filter(course=c).exists():
                possible_tutors[c] = set(ModulePossibleTutors.objects.get(course=c).possible_tutors.all())
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


class TTModel(object):
    def __init__(self, department_abbrev, weeks, year,
                 train_prog=None,
                 stabilize_work_copy=None,
                 min_nps_i=1.,
                 min_bhd_g=1.,
                 min_bd_i=1.,
                 min_bhd_i=1.,
                 min_nps_c=1.,
                 max_stab=5.,
                 lim_ld=1.,
                 core_only=False,
                 send_mails=False):
        print("\nLet's start weeks #%s" % weeks)
        # beg_file = os.path.join('logs',"FlOpTT")
        self.model = LpProblem("FlOpTT", LpMinimize)
        self.min_ups_i = min_nps_i
        self.min_bhd_g = min_bhd_g
        self.min_bd_i = min_bd_i
        self.min_bhd_i = min_bhd_i
        self.min_ups_c = min_nps_c
        self.max_stab = max_stab
        self.lim_ld = lim_ld
        self.core_only = core_only
        self.send_mails = send_mails
        self.var_nb = 0
        self.constraint_nb = 0
        if type(weeks) is int:
            self.weeks = [weeks]
        else:
            try:
                self.weeks = list(weeks)
            except TypeError:
                raise TypeError("Weeks has to be int or iterable")
        self.year = year
        self.warnings = {}

        self.department = Department.objects.get(abbrev=department_abbrev)
        if train_prog is None:
            train_prog = TrainingProgramme.objects.filter(department=self.department)
        try:
            _ = iter(train_prog)
        except TypeError:
            train_prog = TrainingProgramme.objects.filter(id=train_prog.id)
        self.train_prog = train_prog
        self.stabilize_work_copy = stabilize_work_copy
        self.obj = self.lin_expr()
        self.wdb = self.wdb_init()
        self.cost_I, self.FHD_G, self.cost_G, self.cost_SL = self.costs_init()
        self.TT, self.TTrooms , self.TTinstructors = self.TT_vars_init()
        self.IBD, self.IBD_GTE, self.IBHD, self.GBHD, self.IBS, self.forced_IBD = self.busy_vars_init()

        self.avail_instr, self.unp_slot_cost \
            = self.compute_non_prefered_slot_cost()

        self.unp_slot_cost_course, self.avail_course \
            = self.compute_non_prefered_slot_cost_course()

        self.avail_room = self.compute_avail_room()

        # Hack : permet que ça marche même si les dispos sur la base sont pas complètes
        for i in self.wdb.instructors:
            for sl in self.wdb.slots:
                if sl not in self.avail_instr[i]:
                    self.avail_instr[i][sl] = 0
                if sl not in self.unp_slot_cost[i]:
                    self.unp_slot_cost[i][sl] = 0

        self.add_TT_constraints()

        if self.warnings:
            print("Relevant warnings :")
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

        if settings.DEBUG:
            self.model.writeLP('FlOpEDT.lp')

        if self.send_mails:
            self.send_lack_of_availability_mail()


    def wdb_init(self):
        wdb = WeekDB(self.department, self.weeks, self.year, self.train_prog)
        return wdb

    def costs_init(self):
        cost_I = dict(list(zip(self.wdb.instructors,
                               [{week: self.lin_expr() for week in self.weeks + [None]} for _ in self.wdb.instructors])))
        FHD_G = {}
        for apm in [Time.AM, Time.PM]:
            FHD_G[apm] = dict(
                list(zip(self.wdb.basic_groups,
                         [{week: self.lin_expr() for week in self.weeks} for _ in self.wdb.basic_groups])))

        cost_G = dict(
            list(zip(self.wdb.basic_groups,
                     [{week: self.lin_expr() for week in self.weeks + [None]} for _ in self.wdb.basic_groups])))

        cost_SL = dict(
            list(zip(self.wdb.slots,
                     [self.lin_expr() for _ in self.wdb.slots])))
        return cost_I, FHD_G, cost_G, cost_SL

    def TT_vars_init(self):
        TT = {}
        TTrooms = {}
        TTinstructors = {}

        for sl in self.wdb.slots:
            for c in self.wdb.compatible_courses[sl]:
                # print c, c.room_type
                TT[(sl, c)] = self.add_var("TT(%s,%s)" % (sl, c))
                for rg in self.wdb.room_groups_for_type[c.room_type]:
                    TTrooms[(sl, c, rg)] \
                        = self.add_var("TTroom(%s,%s,%s)" % (sl, c, rg))
                for i in self.wdb.possible_tutors[c]:
                    TTinstructors[(sl, c, i)] \
                        = self.add_var("TTinstr(%s,%s,%s)" % (sl, c, i))
        return TT, TTrooms, TTinstructors

    def busy_vars_init(self):
        IBS = {}
        for i in self.wdb.instructors:
            for sl in self.wdb.slots:
                IBS[(i, sl)] = self.add_var("IBS(%s,%s)" % (i, sl))
                # Linking the variable to the TT
                expr = self.lin_expr()
                expr += 100 * IBS[(i, sl)]
                for s_sl in self.wdb.slots_intersecting[sl] | {sl}:
                    for c in self.wdb.possible_courses[i] & self.wdb.compatible_courses[s_sl]:
                        expr -= self.TTinstructors[(s_sl, c, i)]
                self.add_constraint(expr, '<=', 99, "IBS_sup(%s,%s)" % (i, sl))
                self.add_constraint(expr, '>=', 0, "IBS_inf(%s,%s)" % (i, sl))

        IBD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                IBD[(i, d)] = self.add_var("IBD(%s,%s)" % (i, d))
                # Linking the variable to the TT
                dayslots = self.wdb.slots_by_day[d]
                card = 2 * len(dayslots)
                expr = self.lin_expr()
                expr += card * IBD[(i, d)]
                for c in self.wdb.possible_courses[i]:
                    for sl in dayslots & self.wdb.compatible_slots[c]:
                        expr -= self.TTinstructors[(sl, c, i)]
                # Be careful, here as elsewhere, being a supp_tutor is not a possibility, it is necessary...
                for c in self.wdb.courses_for_supp_tutor[i]:
                    for sl in dayslots & self.wdb.compatible_slots[c]:
                        expr -= self.TT[(sl, c)]
                self.add_constraint(expr, '>=', 0)

                if self.wdb.fixed_courses.filter(Q(course__tutor=i) | Q(tutor=i),
                                                 day=d) \
                        or self.wdb.other_departments_sched_courses.filter(Q(course__tutor=i) | Q(tutor=i), day=d):
                        self.add_constraint(IBD[(i, d)], '==', 1)
                        # This next constraint impides to force IBD to be 1
                        # (if there is a meeting, for example...)
                        #self.add_constraint(expr, '<=', card-1)

        forced_IBD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                if self.wdb.sched_courses.filter(day=d.day, course__week=d.week,
                                                 course__suspens=False,
                                                 course__tutor=i).exists():
                    forced_IBD[(i, d)] = 1
                else:
                    forced_IBD[(i, d)] = 0

        IBD_GTE = {week : [] for week in self.weeks}
        max_days = len(TimeGeneralSettings.objects.get(department=self.department).days)
        for week in self.weeks:
            for j in range(max_days + 1):
                IBD_GTE[week].append({})

            for i in self.wdb.instructors:
                for j in range(1, max_days + 1):
                    IBD_GTE[week][j][i] = self.add_floor(str(i) + str(j),
                                                         self.sum(IBD[(i, d)]
                                                                  for d in days_filter(self.wdb.days, week=week)),
                                                         j,
                                                         max_days)

        IBHD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                # add constraint linking IBHD to TT
                for apm in [Time.AM, Time.PM]:
                    IBHD[(i, d, apm)] \
                        = self.add_var("IBHD(%s,%s,%s)" % (i, d, apm))
                    halfdayslots = self.wdb.slots_by_half_day[(d, apm)]
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * IBHD[(i, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.possible_courses[i] & self.wdb.compatible_courses[sl]:
                            expr -= self.TTinstructors[(sl, c, i)]
                    self.add_constraint(expr, '>=', 0)
                    # This constraint impides to force IBHD to be 1
                    # (if there is a meeting, for example...)
                    if self.wdb.fixed_courses.filter(course__tutor=i,
                                                     course__week=d.week,
                                                     day=d.day):
                        # ,creneau__heure__apm=apm):
                        self.add_constraint(IBHD[(i, d, apm)], '==', 1)
                    else:
                        self.add_constraint(expr, '<=', card - 1)

        GBHD = {}
        for g in self.wdb.basic_groups:
            for d in self.wdb.days:
                # add constraint linking IBD to EDT
                for apm in [Time.AM, Time.PM]:
                    GBHD[(g, d, apm)] \
                        = self.add_var("GBHD(%s,%s,%s)" % (g, d, apm))
                    halfdayslots = self.wdb.slots_by_half_day[(d, apm)]
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * GBHD[(g, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.courses_for_group[g] & self.wdb.compatible_courses[sl]:
                            expr -= self.TT[(sl, c)]
                        for sg in g.ancestor_groups():
                            for c in self.wdb.courses_for_group[sg] & self.wdb.compatible_courses[sl]:
                                expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0)
                    self.add_constraint(expr, '<=', card - 1)
        return IBD, IBD_GTE, IBHD, GBHD, IBS, forced_IBD

    def add_var(self, name):
        """
        Create a PuLP binary variable
        """
        # return LpVariable(name, lowBound = 0, upBound = 1, cat = LpBinary)
        countedname = name + '_' + str(self.var_nb)
        self.var_nb += 1
        return LpVariable(countedname, cat=LpBinary)

    def add_constraint(self, expr, relation, value, name=None):
        """
        Add a constraint to the model
        """
        if name is None:
            name = "C_%g" % self.constraint_nb
        if relation == '==':
            pulp_relation = LpConstraintEQ
        elif relation == '<=':
            pulp_relation = LpConstraintLE
        elif relation == '>=':
            pulp_relation = LpConstraintGE
        else:
            raise Exception("relation must be either '==' or '>=' or '<='")

        self.model += LpConstraint(e=expr, sense=pulp_relation,
                                   rhs=value, name=name)  # + '_' + str(self.constraint_nb))
        self.constraint_nb += 1

    def lin_expr(self, expr=None):
        return LpAffineExpression(expr)

    def sum(self, *args):
        return lpSum(list(*args))

    def check_and_sum(self, dict, *args):
        """
        This helper method get a variable list check if the corresponding
        expression exists in the given dict and returns the lpSum of
        available expressions
        """
        expressions = [dict(v) for v in args if v in dict]
        return lpSum(expressions)

    def get_var_value(self, ttvar):
        return round(ttvar.value())

    def get_expr_value(self, ttexpr):
        return ttexpr.value()

    def get_obj_coeffs(self):
        """
        get the coeff of each var in the objective
        """
        l = [(weight, var) for (var, weight) in self.obj.items()
             if var.value() != 0 and round(weight) != 0]
        l.sort(reverse=True)
        return l

    def set_objective(self, obj):
        self.model.setObjective(obj)

    def get_constraint(self, name):
        return self.model.constraints[name]

    def get_all_constraints(self):
        return self.model.constraints

    def remove_constraint(self, constraint_name):
        del self.model.constraints[constraint_name]

    def var_coeff(self, var, constraint):
        return constraint[var]

    def change_var_coeff(self, var, constraint, newvalue):
        constraint[var] = newvalue

    def add_conjunct(self, v1, v2):
        """
        Crée une nouvelle variable qui est la conjonction des deux
        et l'ajoute au modèle
        """
        l_conj_var = self.add_var("%s AND %s" % (str(v1), str(v2)))
        self.add_constraint(l_conj_var - (v1 + v2), '>=', -1)
        self.add_constraint(2 * l_conj_var - (v1 + v2), '<=', 0)
        return l_conj_var

    def add_floor(self, name, expr, floor, bound):
        """
        Add a variable that equals 1 if expr >= floor, is integer expr is
        known to be within [0, bound]
        """
        l_floor = self.add_var("FLOOR %s %d" % (name, floor))
        self.add_constraint(expr - l_floor * floor, '>=', 0)
        self.add_constraint(l_floor * bound - expr, '>=', 1 - floor)
        return l_floor

    def add_if_var_a_then_not_vars_b_constraint(self, var_a, vars_b_list, name_of_b_list=None):
        bound = len(vars_b_list) + 1
        if name_of_b_list is None:
            name_of_b_list = "anonymous list"
        self.add_constraint(
            bound * var_a
            +
            self.sum(var for var in vars_b_list),
            '<=',
            bound,
            'If %s then not any of %s_%g' % (var_a, name_of_b_list, self.constraint_nb))

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost, week=None):
        self.cost_I[instructor][week] += cost

    def add_to_group_cost(self, group, cost, week=None):
        self.cost_G[group][week] += cost

    def add_warning(self, key, warning):
        if key in self.warnings:
            self.warnings[key].append(warning)
        else:
            self.warnings[key] = [warning]

    def add_stabilization_constraints(self):
        if len(self.train_prog) < TrainingProgramme.objects.count():
            print('Will modify only courses of training programme(s)', self.train_prog)

        # maximize stability
        if self.stabilize_work_copy is not None:
            s = Stabilize(general=True,
                          work_copy=self.stabilize_work_copy)
            s.save()
            for week in self.weeks:
                s.enrich_model(self, week, self.max_stab)
            s.delete()
            print('Will stabilize from remote work copy #', \
                  self.stabilize_work_copy)
        else:
            print('No stabilization')

    def add_core_constraints(self):
        """
        Add the core constraints to the PuLP model :
            - a course is scheduled once and only once
            - no group has two courses in parallel
            - + a teacher does not have 2 courses in parallel
              + the teachers are available on the chosen slots
            - no course on vacation days
        """

        print("adding core constraints")

        # This constraint is superfleous because of slot compatibility definition
        # print('Slot_type constraints')
        # for c in self.wdb.courses:
        #     name = 'slot_type_' + str(c)
        #     self.add_constraint(
        #         self.sum([self.TT[(sl, c)] for ct in self.wdb.course_types.exclude(id=c.type.id)
        #                   for sl in filter(self.wdb.slots, course_type=ct)])
        #         + self.sum([self.TT[(sl, c)] for sl in self.wdb.slots if sl.duration != c.type.duration]),
        #         '==',
        #         0,
        #        name=name)

        # constraint : only one course on simultaneous slots
        print('Simultaneous slots constraints for groups')
        for sl1 in self.wdb.slots:
            for bg in self.wdb.basic_groups:
                name = 'simul_slots' + bg.full_name() + '_' + str(sl1)
                self.add_constraint(1000 * self.sum(self.TT[(sl1, c1)] for c1 in self.wdb.courses_for_basic_group[bg]
                                                    & self.wdb.compatible_courses[sl1]) +
                                    self.sum(self.TT[(sl2, c2)] for sl2 in self.wdb.slots_intersecting[sl1] - {sl1}
                                             for c2 in self.wdb.courses_for_basic_group[bg]
                                             & self.wdb.compatible_courses[sl2]),
                                    '<=', 1000, name=name)

        # a course is scheduled once and only once
        for c in self.wdb.courses:
            name = 'core_course_' + str(c) + str(self.constraint_nb)
            self.add_constraint(
                self.sum([self.TT[(sl, c)] for sl in self.wdb.compatible_slots[c]]),
                '==',
                1,
                name=name)

        # Training half day
        for training_half_day in self.wdb.training_half_days:
            training_slots = slots_filter(self.wdb.slots, week_day=training_half_day.day, week=training_half_day.week)
            if training_half_day.apm is not None:
                training_slots = slots_filter(training_slots, apm=training_half_day.apm)
            training_progs = self.train_prog
            if training_half_day.train_prog is not None:
                training_progs = [training_half_day.train_prog]
            self.add_constraint(self.sum(self.TT[(sl, c)] for sl in training_slots
                                         for c in self.wdb.compatible_courses[sl]
                                         & set(self.wdb.courses.filter(group__train_prog__in=training_progs))),
                                '==', 0, "no_course_on_%s_%s_%g" %
                                (training_half_day.day, training_half_day.apm, self.constraint_nb))

    def add_instructors_constraints(self):
        print("adding instructors constraints")
        for c in self.wdb.courses:
            for sl in self.wdb.compatible_slots[c]:
                self.add_constraint(self.sum(self.TTinstructors[(sl, c, i)]
                                             for i in self.wdb.possible_tutors[c]) - self.TT[sl, c],
                                    '==', 0, "Each_course_to_one_tutor %s-%s_%g" % (c, sl, self.constraint_nb))
            if c.supp_tutor.exists():
                supp_tutors = set(c.supp_tutor.all()) & self.wdb.instructors
                if supp_tutors:
                    for sl in self.wdb.compatible_slots[c]:
                        self.add_constraint(1000 * self.TT[(sl, c)]
                                            + self.sum(self.TTinstructors[(sl2, c2, supp_tutor)]
                                                       for supp_tutor in supp_tutors
                                                       for sl2 in self.wdb.slots_intersecting[sl] - {sl}
                                                       for c2 in self.wdb.possible_courses[supp_tutor] &
                                                       self.wdb.compatible_courses[sl2]),
                                            '<=',
                                            1000 * min(self.avail_instr[s_t][sl] for s_t in supp_tutors),
                                            f"No course simultaneous to {sl} for {c}'s supp_tutors")

        for i in self.wdb.instructors:
            for sl in self.wdb.slots:
                name = 'core_instr_' + str(i) + '_' + str(sl)
                self.add_constraint(self.sum(self.TTinstructors[(sl, c, i)]
                                             for c in (self.wdb.compatible_courses[sl]
                                                       & self.wdb.possible_courses[i])),
                                    '<=',
                                    self.avail_instr[i][sl],
                                    name=name)
                name = 'simul_slots' + str(i) + '_' + str(sl)
                self.add_constraint(1000 * self.sum(self.TTinstructors[(sl, c1, i)]
                                                    for c1 in self.wdb.possible_courses[i]
                                                    & self.wdb.compatible_courses[sl])
                                    +
                                    self.sum(self.TTinstructors[(sl2, c2, i)]
                                             for sl2 in self.wdb.slots_intersecting[sl] - {sl}
                                             for c2 in self.wdb.possible_courses[i] & self.wdb.compatible_courses[sl2]),
                                    '<=', 1000, name=name)

    def add_rooms_constraints(self):
        print("adding room constraints")
        # constraint Rooms : there are enough rooms of each type for each slot

        # constraint : each Room is only used once on simultaneous slots
        for r in self.wdb.rooms:
            for sl1 in self.wdb.slots:
                name = 'simul_slots_rooms' + str(r) + '_' + str(sl1)
                self.add_constraint(1000 * self.sum(self.TTrooms[(sl1, c, rg)]
                                                    for (c, rg) in self.wdb.room_course_compat[r]
                                                    if c in self.wdb.compatible_courses[sl1]) +
                                    self.sum(self.TTrooms[(sl2, c, rg)]
                                             for sl2 in self.wdb.slots_intersecting[sl1] - {sl1}
                                             for (c, rg) in self.wdb.room_course_compat[r]
                                             if c in self.wdb.compatible_courses[sl2]),
                                    '<=', 1000, name=name)

        for sl in self.wdb.slots:
            # constraint : each course is assigned to a RoomGroup
            for c in self.wdb.compatible_courses[sl]:
                name = 'core_roomtype_' + str(c) + '_' + str(sl) + '_' + str(self.constraint_nb)
                self.add_constraint(
                    self.sum(self.TTrooms[(sl, c, rg)] for rg in self.wdb.course_rg_compat[c]) - self.TT[(sl, c)],
                    '==',
                    0,
                    name=name)

            # constraint : fixed_courses rooms are not available
            for rg in self.wdb.room_groups:
                fcrg = set(fc for fc in self.wdb.fixed_courses_for_slot[sl] if fc.room == rg)
                # if self.wdb.fixed_courses.filter((Q(start_time__lt=sl.start_time + sl.duration) |
                #                                   Q(start_time__gt=sl.start_time - F('course__type__duration'))),
                #                                  room=rg, day=sl.day).exists():
                if fcrg:
                    for r in rg.subrooms.all():
                        name = 'fixed_room' + str(r) + '_' + str(sl) + '_' + str(self.constraint_nb)
                        self.add_constraint(self.sum(self.TTrooms[(s_sl, c, room)]
                                                     for s_sl in self.wdb.slots_intersecting[sl]
                                                     for c in self.wdb.compatible_courses[s_sl]
                                                     for room in self.wdb.course_rg_compat[c]
                                                     if r in room.subrooms.all()),
                                            '==',
                                            0,
                                            name=name)

            # constraint : each Room is only used once and only when available
            for r in self.wdb.rooms:
                self.add_constraint(
                    self.sum(self.TTrooms[(sl, c, rg)]
                             for (c, rg) in self.wdb.room_course_compat[r]
                             if c in self.wdb.compatible_courses[sl]),
                    '<=',
                    self.avail_room[r][sl],
                    name='core_room_' + str(r) + '_' + str(sl) + '_' + str(self.constraint_nb))

            ########TO BE CHECKED################
            # constraint : respect preference order,
            # if preferred room is available
            for rp in self.wdb.room_prefs:
                e = self.sum(
                    self.TTrooms[(sl, c, rp.unprefer)]
                    for c in set(self.wdb.courses.filter(room_type=rp.for_type)) & self.wdb.compatible_courses[sl])
                preferred_is_unavailable = False
                for r in rp.prefer.subrooms.all():
                    if not self.avail_room[r][sl]:
                        preferred_is_unavailable = True
                        break
                    e -= self.sum(self.TTrooms[(sl, c, rg)]
                                  for (c, rg) in self.wdb.room_course_compat[r]
                                  if c in self.wdb.compatible_courses[sl])
                if preferred_is_unavailable:
                    continue
                # print "### slot :", sl, rp.unprefer, "after", rp.prefer
                # print e <= 0
                self.add_constraint(
                    e,
                    '<=',
                    0
                )

    # constraint : respect preference order with full order for each room type :
    # perfs OK
    # for rt in self.wdb.room_types:
    #     l=[]
    #     for rgp in rt.members.all():
    #         if len(l)>0:
    #             for rgp_before in l:
    #                 e = quicksum(self.TTrooms[(sl, c, rgp)]
    #                              for c in self.wdb.courses.filter(room_type=rt))
    #                 preferred_is_unavailable = False
    #                 for r in rgp_before.subrooms.all():
    #                     if len(db.RoomUnavailability.objects.filter(
    #                                   week=self.weeks, year=self.year,
    #                                   creneau=sl, room=r)) > 0:
    #                         # print r, "unavailable for ",sl
    #                         preferred_is_unavailable = True
    #                         break
    #                     e -= quicksum(self.TTrooms[(sl, c, rg)] for (c, rg) in
    #                                   room_course_compat[r])
    #                 if preferred_is_unavailable:
    #                     continue
    #                 self.add_constraint(
    #                     e,
    #                     GRB.LESS_EQUAL,
    #                     0
    #                 )
    #         l.append(rgp)

    def add_dependency_constraints(self, weight=None):
        """
        Add the constraints of dependency saved on the DB:
        -include dependencies
        -include non same-day constraint
        -include simultaneity (double dependency)
        If there is a weight, it's a preference, else it's a constraint...
        """
        print('adding dependency constraints')
        for p in self.wdb.dependencies:
            c1 = p.course1
            c2 = p.course2
            if c1 == c2:
                print("Warning: %s is declared depend on itself" % c1)
                continue
            for sl1 in self.wdb.compatible_slots[c1]:
                for sl2 in self.wdb.compatible_slots[c2]:
                    if not sl2.is_after(sl1) \
                            or (p.ND and (sl2.day == sl1.day)) \
                            or (p.successive and not sl2.is_successor_of(sl1)):
                        if not weight:
                            self.add_constraint(self.TT[(sl1, c1)]
                                                + self.TT[(sl2, c2)], '<=', 1,
                                                "Dependency %s %g" % (p, self.constraint_nb))
                        else:
                            conj_var = self.add_conjunct(self.TT[(sl1, c1)],
                                                         self.TT[(sl2, c2)])
                            self.obj += conj_var * weight
                    if p.successive and sl2.is_successor_of(sl1):
                        for rg1 in self.wdb.room_groups_for_type[c1.room_type]:
                            for rg2 in self.wdb.room_groups_for_type[c2.room_type].exclude(id=rg1.id):
                                self.add_constraint(self.TTrooms[(sl1, c1, rg1)]
                                                    + self.TTrooms[(sl2, c2, rg2)], '<=', 1)

    def send_unitary_lack_of_availability_mail(self, tutor, week, available_hours, teaching_hours,
                                               prefix="[flop!EDT] "):
        subject = f"Manque de dispos semaine {week}"
        message = f"Bonjour {tutor.first_name}\n" \
                  f"Semaine {week} vous ne donnez que {available_hours} heures de disponibilités, " \
                  f"alors que vous êtes censé⋅e assurer {teaching_hours} heures de cours...\n" \
                  f"Est-ce que vous avez la possibilité d'ajouter des créneaux de disponibilité ?\n" \
                  f"Sinon, pouvez-vous s'il vous plaît décaler des cours à une semaine précédente ou suivante ?\n" \
                  f"Merci d'avance.\n" \
                  f"Les gestionnaires d'emploi du temps."
        email = EmailMessage(
            prefix + subject,
            "(Cet e-mail vous a été envoyé automatiquement par le générateur "
            "d'emplois du temps du logiciel flop!EDT)\n\n"
            + message +
            "\n\nPS: Attention, cet email risque de vous être renvoyé à chaque prochaine génération "
            "d'emploi du temps si vous n'avez pas fait les modifications attendues...\n"
            "N'hésitez pas à nous contacter en cas de souci.",
            to=(tutor.email,)
        )
        email.send()

    def send_lack_of_availability_mail(self, prefix="[flop!EDT] "):
        for key in self.warnings:
            if key in self.wdb.instructors:
                for w in self.warnings[key]:
                    if ' < ' in w:
                        data = w.split(' ')
                        self.send_unitary_lack_of_availability_mail(key, data[-1], data[0], data[4],
                                                                    prefix=prefix)


    def compute_non_prefered_slot_cost(self):
        """
        Returns:
            - UnpSlotCost : a 2 level-dictionary
                            { teacher => slot => cost (float in [0,1])}}
            - availInstr : a 2 level-dictionary { teacher => slot => 0/1 }

        The slot cost will be:
            - 0 if it is a prefered slot
            - max(0., 2 - slot value / (average of slot values) )
        """

        avail_instr = {}
        unp_slot_cost = {}
        # dict(zip(instructors,
        #          [dict(zip(mm.disponibilite.objects.filter(),[for sl in ]))
        #           for i in instructors]))
        # unpreferred slots for an instructor costs
        # min((float(nb_avail_slots) / min(2*nb_teaching_slots,22)),1)
        holidays = [h.day for h in self.wdb.holidays]

        if self.wdb.holidays:
            self.add_warning(None, "%s are holidays" % holidays)

        for i in self.wdb.instructors:
            avail_instr[i] = {}
            unp_slot_cost[i] = {}
            for week in self.weeks:
                week_slots = slots_filter(self.wdb.slots, week=week)
                teaching_duration = sum(c.type.duration
                                        for c in self.wdb.courses_for_tutor[i] if c.week == week)
                total_teaching_duration = teaching_duration + sum(c.type.duration
                                                                  for c in self.wdb.other_departments_courses_for_tutor[i]
                                                                  if c.week == week)

                if days_filter(self.wdb.holidays, week=week):
                    week_tutor_availabilities = set(a for a in self.wdb.availabilities[i][week] if a.day not in holidays)
                else:
                    week_tutor_availabilities = self.wdb.availabilities[i][week]

                if not week_tutor_availabilities:
                    self.add_warning(i, "no availability information given week %g" % week)
                    for sl in week_slots:
                        unp_slot_cost[i][sl] = 0
                        avail_instr[i][sl] = 1

                else:
                    avail_time = sum(a.duration for a in week_tutor_availabilities if a.value >= 1)
                    maximum = max([a.value for a in week_tutor_availabilities])
                    non_prefered_duration = max(1, sum(a.duration
                                                       for a in week_tutor_availabilities if 1 <= a.value <= maximum - 1))

                    if avail_time < teaching_duration:
                        self.add_warning(i, "%g available hours < %g courses hours week %g" %
                                         (avail_time/60, teaching_duration/60, week))
                        for sl in week_slots:
                            unp_slot_cost[i][sl] = 0
                            avail_instr[i][sl] = 1

                    elif avail_time < total_teaching_duration:
                        self.add_warning(i, "%g available hours < %g courses hours including other deps week %g" % (
                            avail_time / 60, total_teaching_duration / 60, week))
                        for sl in week_slots:
                            unp_slot_cost[i][sl] = 0
                            avail_instr[i][sl] = 1

                    else:
                        average_value = sum(a.duration * a.value
                                            for a in week_tutor_availabilities
                                            if 1 <= a.value <= maximum - 1) / non_prefered_duration
                        if average_value == maximum:
                            for sl in week_slots:
                                unp_slot_cost[i][sl] = 0
                                avail_instr[i][sl] = 1
                            continue
                        for sl in week_slots:
                            avail = set(a for a in week_tutor_availabilities
                                        if a.start_time < sl.end_time and sl.start_time < a.start_time + a.duration
                                        and a.day == sl.day.day)
                            if not avail:
                                print("availability pbm for %s slot %s" % (i, sl))
                                unp_slot_cost[i][sl] = 0
                                avail_instr[i][sl] = 1
                            else:
                                minimum = min(a.value for a in avail)
                                if minimum == 0:
                                    avail_instr[i][sl] = 0
                                    unp_slot_cost[i][sl] = 0
                                else:
                                    avail_instr[i][sl] = 1
                                    value = minimum
                                    if value == maximum:
                                        unp_slot_cost[i][sl] = 0
                                    else:
                                        unp_slot_cost[i][sl] = (value - maximum) / (average_value - maximum)

                        if teaching_duration / 60 < 9 and avail_time < 2 * teaching_duration \
                                and i.status == Tutor.FULL_STAFF:
                            self.add_warning(i, "only %g available hours for %g courses hours week %g" %
                                             (avail_time / 60,
                                              teaching_duration / 60,
                                              week))
                            for sl in week_slots:
                                unp_slot_cost[i][sl] = 0

        return avail_instr, unp_slot_cost

    def compute_non_prefered_slot_cost_course(self):
        """
         :returns
         non_prefered_slot_cost_course :a 2 level dictionary
         { (CourseType, TrainingProgram)=> { Non-prefered slot => cost (float in [0,1])}}

         avail_course : a 2 level-dictionary
         { (CourseType, TrainingProgram) => slot => availability (0/1) }
        """

        non_prefered_slot_cost_course = {}
        avail_course = {}
        for course_type in self.wdb.course_types:
            for promo in self.train_prog:
                for week in self.weeks:
                    avail_course[(course_type, promo)] = {}
                    non_prefered_slot_cost_course[(course_type, promo)] = {}
                    courses_avail = set(self.wdb.courses_availabilities
                                        .filter(course_type=course_type,
                                                train_prog=promo,
                                                week=week))
                    if not courses_avail:
                        courses_avail = set(self.wdb.courses_availabilities
                                            .filter(course_type=course_type,
                                                    train_prog=promo,
                                                    week=None))
                    if not courses_avail:
                        print("No course availability given for %s - %s" % (course_type, promo))
                        for sl in self.wdb.slots:
                            avail_course[(course_type, promo)][sl] = 1
                            non_prefered_slot_cost_course[(course_type,
                                                           promo)][sl] = 0
                    else:
                        for sl in self.wdb.slots:
                            try:
                                avail = set(a for a in courses_avail
                                            if a.start_time < sl.end_time and sl.start_time < a.start_time + a.duration
                                                and a.day == sl.day.day)
                                if avail:
                                    minimum = min(a.value for a in avail)
                                    if minimum == 0:
                                        avail_course[(course_type, promo)][sl] = 0
                                        non_prefered_slot_cost_course[(course_type,
                                                                       promo)][sl] = 5
                                    else:
                                        avail_course[(course_type, promo)][sl] = 1
                                        value = minimum
                                        non_prefered_slot_cost_course[(course_type, promo)][sl] \
                                            = 1 - value / 8

                                else:
                                    avail_course[(course_type, promo)][sl] = 1
                                    non_prefered_slot_cost_course[(course_type, promo)][sl] = 0

                            except:
                                avail_course[(course_type, promo)][sl] = 1
                                non_prefered_slot_cost_course[(course_type, promo)][sl] = 0
                                print("Course availability problem for %s - %s on start time %s" % (course_type, promo, sl))

        return non_prefered_slot_cost_course, avail_course

    def compute_avail_room(self):
        avail_room = {}
        for room in self.wdb.rooms:
            avail_room[room] = {}
            for sl in self.wdb.slots:
                if RoomPreference.objects.filter(
                        start_time__lt=sl.start_time + sl.duration,
                        start_time__gt=sl.start_time - F('duration'),
                        day=sl.day.day,
                        week=sl.day.week,
                        year=self.year,
                        room=room, value=0).exists():
                    avail_room[room][sl] = 0
                else:
                    avail_room[room][sl] = 1

        return avail_room

    def add_slot_preferences(self):
        """
         Add the constraints derived from the slot preferences expressed on the database
         """
        print("adding slot preferences")
        # first objective  => minimise use of unpreferred slots for teachers
        # ponderation MIN_UPS_I
        for i in self.wdb.instructors:
            M = MinNonPreferedSlot(tutor=i,
                                   weight=max_weight)
            for week in self.weeks:
                M.enrich_model(self, week,
                               ponderation=self.min_ups_i)

        # second objective  => minimise use of unpreferred slots for courses
        # ponderation MIN_UPS_C
        for promo in self.train_prog:
            M = MinNonPreferedSlot(train_prog=promo,
                                   weight=max_weight)
            for week in self.weeks:
                M.enrich_model(self, week,
                               ponderation=self.min_ups_c)

    def add_other_departments_constraints(self):
        """
        Add the constraints imposed by other departments' scheduled courses.
        """
        print("adding other departments constraints")
        for sl in self.wdb.slots:
            # constraint : other_departments_sched_courses rooms are not available
            for r in self.wdb.rooms:
                occupied_in_another_department = False
                for sc in self.wdb.other_departments_sched_courses_for_room[r]:
                    if sl.day.day == sc.day and sl.day.week == sc.course.week and \
                            (sc.start_time < sl.end_time
                             and sl.start_time < sc.start_time + sc.course.type.duration):
                        occupied_in_another_department = True
                if occupied_in_another_department:
                    name = 'other_dep_room_' + str(r) + '_' + str(sl) + '_' + str(self.constraint_nb)
                    self.add_constraint(self.sum(self.TTrooms[(sl, c, room)]
                                                 for c in self.wdb.compatible_courses[sl]
                                                 for room in self.wdb.course_rg_compat[c]
                                                 if r in room.subrooms.all()),
                                        '==',
                                        0,
                                        name=name)

            # constraint : other_departments_sched_courses instructors are not available
            for i in self.wdb.instructors:
                occupied_in_another_department = False
                for sc in self.wdb.other_departments_scheduled_courses_for_tutor[i]:
                    if sl.day.day == sc.day and sl.day.week == sc.course.week and \
                            (sc.start_time < sl.end_time
                             and sl.start_time < sc.start_time + sc.course.type.duration):
                        occupied_in_another_department = True
                if occupied_in_another_department:
                    name = 'other_dep_' + str(i) + '_' + str(sl) + '_' + str(self.constraint_nb)
                    self.add_constraint(self.sum(self.TT[(sl, c)]
                                                 for c in (self.wdb.courses_for_tutor[i]
                                                           | self.wdb.courses_for_supp_tutor[i]) &
                                                 self.wdb.compatible_courses[sl]),
                                        '==',
                                        0,
                                        name=name)
                    self.add_constraint(self.IBD[(i, sl.day)], '==', 1)

    def add_specific_constraints(self):
        """
        Add the active specific constraints stored in the database.
        """
        print("adding active specific constraints")
        for promo in self.train_prog:
            for week in self.weeks:
                for constr in get_constraints(
                                self.department,
                                week=week,
                                year=self.year,
                                train_prog=promo,
                                is_active=True):
                    constr.enrich_model(self, week)

    def update_objective(self):
        for week in self.weeks + [None]:
            for i in self.wdb.instructors:
                self.obj += self.cost_I[i][week]
            for g in self.wdb.basic_groups:
                self.obj += self.cost_G[g][week]
        for sl in self.wdb.slots:
            self.obj += self.cost_SL[sl]
        self.set_objective(self.obj)

    def add_TT_constraints(self):
        self.add_stabilization_constraints()

        self.add_core_constraints()

        self.add_dependency_constraints()

        self.add_rooms_constraints()

        self.add_instructors_constraints()

        if self.core_only:
            return

        self.add_other_departments_constraints()

        self.add_slot_preferences()

        self.add_specific_constraints()

    def add_tt_to_db(self, target_work_copy):

        close_old_connections()
        # remove target working copy
        ScheduledCourse.objects \
            .filter(course__module__train_prog__department=self.department,
                    course__week__in=self.weeks,
                    course__year=self.year,
                    work_copy=target_work_copy) \
            .delete()

        for c in self.wdb.courses:
            for sl in self.wdb.compatible_slots[c]:
                for i in self.wdb.possible_tutors[c]:
                    if self.get_var_value(self.TTinstructors[(sl, c, i)]) == 1:
                        # No = len(self.wdb.sched_courses \
                        #          .filter(course__module=c.module,
                        #                  course__group=c.group,
                        #                  course__week__lte=self.weeks - 1,
                        #                  copie_travail=0))
                        # No += len(CoursPlace.objects \
                        #           .filter(course__module=c.module,
                        #                   course__group=c.group,
                        #                   course__week=self.weeks,
                        #                   copie_travail=target_work_copy))
                        cp = ScheduledCourse(course=c,
                                             tutor=i,
                                             start_time=sl.start_time,
                                             day=sl.day.day,
                                             work_copy=target_work_copy)
                        for rg in c.room_type.members.all():
                            if self.get_var_value(self.TTrooms[(sl, c, rg)]) == 1:
                                cp.room = rg
                                break
                        cp.save()

        for fc in self.wdb.fixed_courses:
            cp = ScheduledCourse(course=fc.course,
                                 start_time=fc.start_time,
                                 day=fc.day,
                                 room=fc.room,
                                 work_copy=target_work_copy,
                                 tutor=fc.tutor)
            cp.save()

        # # On enregistre les coûts dans la BDD
        TutorCost.objects.filter(department=self.department,
                                 week__in=self.wdb.weeks,
                                 year=self.wdb.year,
                                 work_copy=target_work_copy).delete()
        GroupFreeHalfDay.objects.filter(group__train_prog__department=self.department,
                                        week__in=self.wdb.weeks,
                                        year=self.wdb.year,
                                        work_copy=target_work_copy).delete()
        GroupCost.objects.filter(group__train_prog__department=self.department,
                                 week__in=self.wdb.weeks,
                                 year=self.wdb.year,
                                 work_copy=target_work_copy).delete()
        for week in self.weeks:
            for i in self.wdb.instructors:
                tc = TutorCost(department=self.department,
                               tutor=i,
                               year=self.wdb.year,
                               week=week,
                               value=self.get_expr_value(self.cost_I[i][week]),
                               work_copy=target_work_copy)
                tc.save()

            for g in self.wdb.basic_groups:
                djlg = GroupFreeHalfDay(group=g,
                                        year=self.wdb.year,
                                        week=week,
                                        work_copy=target_work_copy,
                                        DJL=self.get_expr_value(self.FHD_G[Time.PM][g][week]) +
                                            0.01 * self.get_expr_value(self.FHD_G['AM'][g][week]))
                djlg.save()
                cg = GroupCost(group=g,
                               year=self.wdb.year,
                               week=week,
                               work_copy=target_work_copy,
                               value=self.get_expr_value(self.cost_G[g][week]))
                cg.save()

    def optimize(self, time_limit, solver, presolve=2):

        # The solver value shall be one of the available
        # solver corresponding pulp command or contain
        # gurobi

        
        if 'gurobi' in solver.lower() or hasattr(pulp_solvers, solver):
            # ignore SIGINT while solver is running
            # => SIGINT is still delivered to the solver, which is what we want
            solver = GUROBI_NAME
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.model.solve(GUROBI_CMD(keepFiles=1,
                                        msg=True,
                                        options=[("TimeLimit", time_limit),
                                                 ("Presolve", presolve),
                                                 ("MIPGapAbs", 0.2)]))
        else:
            # raise an exception when the solver name is incorrect
            command = getattr(pulp_solvers, solver)
            self.model.solve(command(keepFiles=1,
                                     msg=True,
                                     presolve=presolve,
                                     maxSeconds=time_limit))
        status = self.model.status
        print(LpStatus[status])
        if status == LpStatusOptimal or (solver != GUROBI_NAME and status == LpStatusNotSolved):
            return self.get_obj_coeffs()

        else:
            print('lpfile has been saved in FlOpTT-pulp.lp')
            return None

    def solve(self, time_limit=3600, target_work_copy=None, solver=GUROBI_NAME):
        """
        Generates a schedule from the TTModel
        The solver stops either when the best schedule is obtained or timeLimit
        is reached.

        If stabilize_work_copy is None: does not move the scheduled courses
        whose year group is not in train_prog and fetches from the remote database
        these scheduled courses with work copy 0.

        If target_work_copy is given, stores the resulting schedule under this
        work copy number.
        If target_work_copy is not given, stores under the lowest working copy
        number that is greater than the maximum work copy numbers for the
        considered week.
        Returns the number of the work copy
        """
        print("\nLet's solve weeks #%s" % self.weeks)

        self.update_objective()

        if target_work_copy is None:
            local_max_wc = ScheduledCourse \
                .objects \
                .filter(
                course__module__train_prog__department=self.department,
                course__week__in=self.weeks,
                course__year=self.year) \
                .aggregate(Max('work_copy'))['work_copy__max']

            if local_max_wc is None:
                local_max_wc = -1

            target_work_copy = local_max_wc + 1

        print("Will be stored with work_copy = #%g" % target_work_copy)

        print("Optimization started at", \
              datetime.datetime.today().strftime('%Hh%M'))
        result = self.optimize(time_limit, solver)
        print("Optimization ended at", \
              datetime.datetime.today().strftime('%Hh%M'))

        if result is not None:
            self.add_tt_to_db(target_work_copy)
            for week in self.weeks:
                reassign_rooms(self.department, week, self.year, target_work_copy)
            return target_work_copy


def get_constraints(department, week=None, year=None, train_prog=None, is_active=None):
    #
    #  Return constraints corresponding to the specific filters
    #
    query = Q(department=department)

    if is_active:
        query &= Q(is_active=is_active)

    if week and not year:
        logger.warning(f"Unable to filter constraint for weeks {week} without specifing year")
        return

    if week and train_prog:
        query &= \
            Q(train_prog__abbrev=train_prog) & Q(week__isnull=True) & Q(year__isnull=True) | \
            Q(train_prog__abbrev=train_prog) & Q(week=week) & Q(year=year) | \
            Q(train_prog__isnull=True) & Q(week=week) & Q(year=year) | \
            Q(train_prog__isnull=True) & Q(week__isnull=True) & Q(year__isnull=True)
    elif week:
        query &= Q(week=week) & Q(year=year) | Q(week__isnull=True) & Q(year__isnull=True)
    elif train_prog:
        query &= Q(train_prog__abbrev=train_prog) | Q(train_prog__isnull=True)

    # Look up the TTConstraint subclasses records to update
    types = TTConstraint.__subclasses__()
    for type in types:
        queryset = type.objects.filter(query)

        # Get prefetch  attributes list for the current type
        atributes = type.get_viewmodel_prefetch_attributes()
        if atributes:
            queryset = queryset.prefetch_related(*atributes)

        for constraint in queryset.order_by('id'):
            yield constraint
