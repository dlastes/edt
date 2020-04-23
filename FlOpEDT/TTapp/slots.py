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
from base.models import Time, Day, TimeGeneralSettings

slot_pause = 30

midday = 12 * 60

basic_slot_duration = 90

days_list = [c[0] for c in Day.CHOICES]
days_index = {}
for c in Day.CHOICES:
    days_index[c[0]] = days_list.index(c[0])


class Slot(object):
    def __init__(self, day, start_time, course_type=None):
        self.course_type = course_type
        if course_type is not None:
            pm_start = TimeGeneralSettings.objects.get(department=course_type.department).lunch_break_finish_time
        else:
            pm_start = midday
        self.day = day
        self.start_time = start_time
        self.duration = basic_slot_duration
        if self.course_type is not None:
            self.duration = self.course_type.duration
        self.end_time = self.start_time + self.duration
        if self.start_time >= pm_start:
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
        hours = self.start_time // 60
        minuts = self.start_time % 60
        if minuts == 0:
            minuts = ''
        return str(self.course_type) + '_' + str(self.day) + '_' + str(hours) + 'h' + str(minuts)

    def __repr__(self):
        return str(self)

    def get_day(self):
        return self.day


def slots_filter(slot_set, day=None, apm=None, course_type=None, start_time=None, week_day=None,
                 simultaneous_to=None, week=None, is_after=None, starts_after=None, starts_before=None,
                 ends_before=None):
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

