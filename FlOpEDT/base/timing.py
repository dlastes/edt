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

def str_to_min(time_string):
    """Convert input time format into minute number

    :param time_string string in hour:minute format
    :return: Integer minutes

    """
    hours_minutes = time_string.split(':')
    return int(hours_minutes[0]) * 60 + int(hours_minutes[1])