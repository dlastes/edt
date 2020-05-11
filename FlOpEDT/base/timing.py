"""
 This file is part of the FlOpEDT/FlOpScheduler project.
 Copyright (c) 2017
 Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public
 License along with this program. If not, see
 <http://www.gnu.org/licenses/>.

 You can be released from the requirements of the license by purchasing
 a commercial license. Buying such a license is mandatory as soon as
 you develop activities involving the FlOpEDT/FlOpScheduler software
 without disclosing the source code of your own applications.

 helpers for time management
 ---------------------------
"""

from enum import Enum


def hr_min(t):
    h = t//60
    m = t - h*60
    return h, m


def hhmm(t):
    h,m = hr_min(t)
    return f'{h:02d}:{m:02d}'


def str_slot(day, start_time, duration):
    return f"{day}. {hhmm(start_time)}" + \
        f"-{hhmm(start_time + duration)}"


def min_to_str(minutes):
    """Convert minute number into input time format

    :param minutes: integer minutes
    :return: string in hour:minute format

    """
    return "%02d:%02d" % hr_min(minutes)


def french_format(minutes):
    """Convert minute number into french time format

    :param minutes: integer minutes
    :return: string in hour h minute format

    """
    result = str(minutes//60) + 'h'
    minutes = minutes % 60
    if 0 < minutes < 10:
        result += '0' + str(minutes)
    elif minutes >= 10:
        result += str(minutes)
    return result


def str_to_min(time_string):
    """Convert input time format into minute number

    :param time_string string in hour:minute format
    :return: Integer minutes

    """
    hours_minutes = time_string.split(':')
    return int(hours_minutes[0]) * 60 + int(hours_minutes[1])


# will not be used
# TO BE DELETED at the end
class Time:
    AM = 'AM'
    PM = 'PM'
    HALF_DAY_CHOICES = ((AM, 'AM'), (PM, 'PM'))


class Day(object):
    MONDAY = "m"
    TUESDAY = "tu"
    WEDNESDAY = "w"
    THURSDAY = "th"
    FRIDAY = "f"
    SATURDAY = "sa"
    SUNDAY = "su"

    CHOICES = ((MONDAY, "monday"), (TUESDAY, "tuesday"),
               (WEDNESDAY, "wednesday"), (THURSDAY, "thursday"),
               (FRIDAY, "friday"), (SATURDAY, "saturday"),
               (SUNDAY, "sunday"))

    def __init__(self, day, week):
        self.day = day
        self.week = week

    def __str__(self):
        # return self.nom[:3]
        return self.day + '_s' + str(self.week)


days_list = [c[0] for c in Day.CHOICES]
days_index = {}
for c in Day.CHOICES:
    days_index[c[0]] = days_list.index(c[0])