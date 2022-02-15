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

from base.models import RoomType, RoomPreference, ScheduledCourse, Department, TrainingProgramme, \
    TutorCost, GroupFreeHalfDay, GroupCost, TimeGeneralSettings, RoomSort, Room

from base.timing import Time, Day
import base.queries as queries

from TTapp.TTConstraint import max_weight
from TTapp.slots import Slot, slots_filter, days_filter

from django.db import close_old_connections
from django.db.models import Q, Max, F

import datetime

from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint

from TTapp.ilp_constraints.constraints.slotInstructorConstraint import SlotInstructorConstraint

from FlOpEDT.decorators import timer

from TTapp.FlopModel import FlopModel, GUROBI_NAME, solution_files_path


class RoomModel(FlopModel):
    @timer
    def __init__(self, department_abbrev, weeks, work_copy=0, keep_many_solution_files=False):
        # beg_file = os.path.join('logs',"FlOpTT")
        self.department = Department.objects.get(abbrev=department_abbrev)
        self.weeks = weeks
        super(RoomModel, self).__init__(keep_many_solution_files=keep_many_solution_files)

        print("\nLet's start rooms affectation for weeks #%s" % self.weeks)
        self.work_copy = work_copy
        self.days, self.slots = self.slots_init()
        self.courses, self.other_departments_located_courses, \
            self.other_departments_located_courses_for_slot = self.courses_init()
        self.room_types, self.rooms, self.basic_rooms, self.rooms_for_type, \
            self.room_course_compat, self.course_room_compat, self.other_departments_located_courses_for_room, \
            self.courses_for_room_type = self.rooms_init()
        self.tutors, self.tutors_room_sorts, self.groups, self.basic_groups, \
            self.all_groups_of, self.basic_groups_of= self.users_init()
        self.cost_I, self.cost_G, self.cost_SL, self.generic_cost = self.costs_init()
        self.TTrooms = self.TTrooms_init()
        self.avail_room = self.compute_avail_room()

        self.add_rooms_constraints()
        self.add_tutors_constraints()
        self.add_specific_constraints()
        if self.warnings:
            print("Relevant warnings :")
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

    def slots_init(self):
        days = [Day(week=week, day=day)
                for week in self.weeks
                for day in TimeGeneralSettings.objects.get(department=self.department).days]

        slots = []
        for day in days:
            courses_of_the_day = self.courses.filter(course__week=day.week, day=day.day)
            if not courses_of_the_day.exists():
                continue
            times_set = set(c.start_time for c in courses_of_the_day) | \
                        set(c.end_time for c in courses_of_the_day)
            times_list = list(times_set)
            times_list.sort()
            for i in range(len(times_list)-1):
                slots.append(Slot(day=day,
                                  start_time=times_list[i],
                                  end_time=times_list[i+1]))
        return days, slots

    def courses_init(self):
        all_courses = ScheduledCourse.objects.filter(course__week__in=self.weeks,
                                                     work_copy=self.work_copy)
        courses = all_courses.filter(course__type__department=self.department) \
            .select_related('course', 'course__room_type')
        all_located_courses = all_courses.exclude(room=None)
        other_departments_located_courses = all_located_courses.exclude(course__type__department=self.department)
        other_departments_located_courses_for_slot = {}
        for sl in self.slots:
            other_departments_located_courses_for_slot[sl] = \
                set(lc for lc in self.other_departments_located_courses
                    if sl.is_simultaneous_to(lc))

        return courses, other_departments_located_courses, other_departments_located_courses_for_slot

    def users_init(self):
        # USERS
        tutors = set(c.course.tutor for c in self.courses.distinct("course__tutor"))
        for course in self.courses.distinct("course__supp_tutor"):
            tutors |= set(course.course.supp_tutor.all())

        tutors_room_sorts = {}
        for tutor in tutors:
            tutors_room_sorts[tutor] = RoomSort.objects.filter(for_type__department=self.department,
                                                               tutor = tutor)

        groups = set()
        for course in self.courses.distinct("course__groups"):
            groups |= set(course.course.groups.all())

        basic_groups = set()
        for g in groups:
            if g.is_structural:
                basic_groups |= g.basic_groups()

        all_groups_of = {}
        for g in basic_groups:
            all_groups_of[g] = g.and_ancestors()

        basic_groups_of = {}
        for g in groups:
            basic_groups_of[g] = set()
            for bg in basic_groups:
                if g in all_groups_of[bg]:
                    basic_groups_of[g].add(bg)

        return tutors, tutors_room_sorts, groups, basic_groups, all_groups_of, basic_groups_of

    def rooms_init(self):
        # ROOMS
        room_types = set(c.course.room_type for c in self.courses.distinct('course__room_type'))

        basic_rooms = queries.get_rooms(self.department.abbrev, basic=True).distinct()
        rooms_for_type = {t: t.members.all() for t in room_types}

        rooms = set(Room.objects.filter(departments=self.department).distinct())
        for room in basic_rooms:
            rooms |= room.and_overrooms()

        course_room_compat = {}
        for course in self.courses:
            course_room_compat[course] = set(course.course.room_type.members.all())

        # for each Room, build the list of courses that may use it
        room_course_compat = {}
        for basic_room in basic_rooms:
            room_course_compat[basic_room] = []
            for room in basic_room.and_overrooms():
                room_course_compat[basic_room].extend(
                    [(course, room) for course in self.courses if room in course_room_compat[course]])

        if self.department.mode.visio:
            for c in self.courses:
                course_room_compat[c].add(None)

        other_departments_located_courses_for_room = {}
        for basic_room in basic_rooms:
            other_departments_located_courses_for_room[basic_room] = set()
            for room in basic_room.and_overrooms():
                other_departments_located_courses_for_room[basic_room] |= set(self.other_departments_located_courses.
                                                                              filter(room=room))

        courses_for_room_type = {}
        for rt in room_types:
            courses_for_room_type[rt] = set(self.courses.filter(course__room_type=rt))

        return room_types, rooms, basic_rooms, rooms_for_type, room_course_compat, course_room_compat, \
               other_departments_located_courses_for_room, courses_for_room_type

    @timer
    def TTrooms_init(self):
        TTrooms = {}
        for course in self.courses:
            for room in self.course_room_compat[course]:
                TTrooms[(course, room)] = self.add_var("TTroom(%s,%s)" % (course, room))
        return TTrooms

    def compute_avail_room(self):
        avail_room = {}
        for room in self.basic_rooms:
            avail_room[room] = {}
            for sl in self.slots:
                if RoomPreference.objects.filter(
                        start_time__lt=sl.start_time + sl.duration,
                        start_time__gt=sl.start_time - F('duration'),
                        day=sl.day.day,
                        week=sl.day.week,
                        room=room, value=0).exists():
                    avail_room[room][sl] = 0
                else:
                    avail_room[room][sl] = 1

        for sl in self.slots:
            # constraint : other_departments_located_courses rooms are not available
            for basic_room in self.basic_rooms:
                other_dep_located_courses = self.other_departments_located_courses_for_room[basic_room] \
                                              & self.other_departments_located_courses_for_slot[sl]
                if other_dep_located_courses:
                    self.avail_room[basic_room][sl] = 0
        return avail_room

    @timer
    def costs_init(self):
        cost_I = dict(list(zip(self.tutors,
                               [{week: self.lin_expr() for week in self.weeks + [None]} for _ in
                                self.tutors])))

        cost_G = dict(
            list(zip(self.basic_groups,
                     [{week: self.lin_expr() for week in self.weeks + [None]} for _ in self.basic_groups])))

        cost_SL = dict(
            list(zip(self.slots,
                     [self.lin_expr() for _ in self.slots])))

        generic_cost = {week: self.lin_expr() for week in self.weeks + [None]}

        return cost_I, cost_G, cost_SL, generic_cost

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost, week=None):
        self.cost_I[instructor][week] += cost

    def add_to_group_cost(self, group, cost, week=None):
        self.cost_G[group][week] += cost

    def add_to_generic_cost(self, cost, week=None):
        self.generic_cost[week] += cost

    @timer
    def add_rooms_constraints(self):
        # constraint : each Room is used at most once, if available, on every slot
        for basic_room in self.basic_rooms:
            for sl in self.slots:
                self.add_constraint(self.sum(self.TTrooms[(course, room)]
                                             for (course, room) in self.room_course_compat[basic_room]
                                             if course.is_simultaneous_to(sl)),
                                    '<=', self.avail_room[basic_room][sl],
                                    Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                               rooms=basic_room, slots=sl))

        # each course is located into a room
        for course in self.courses:
            self.add_constraint(
                self.sum(self.TTrooms[(course, room)] for room in self.course_room_compat[course]),
                '==', 1,
                Constraint(constraint_type=ConstraintType.CORE_ROOMS, courses=course))

    @timer
    def add_tutors_constraints(self):
        pass

    @timer
    def add_specific_constraints(self):
        pass

    def update_objective(self):
        self.obj = self.lin_expr()
        for week in self.weeks + [None]:
            for i in self.tutors:
                self.obj += self.cost_I[i][week]
            for g in self.basic_groups:
                self.obj += self.cost_G[g][week]
            self.obj += self.generic_cost[week]
        for sl in self.slots:
            self.obj += self.cost_SL[sl]
        self.set_objective(self.obj)

