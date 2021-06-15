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


from FlOpEDT.base.timing import Time
from django.db import models

from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint
from django.utils.translation import gettext_lazy as _
from base.models import UserPreference
from base.timing import TimeInterval


# Vérifier que le cours deux peut être mis après le cours 1
## Vérifier la disponibilité des tutors
## Vérifier les créneaux possibles pour les cours

#if successive : vérifier que la fin du premier peut-être juste après un second
#if ND : vérifier que le premier peut être au minimum un jour avant


class Precedence(TTConstraint):
    course1 = models.ForeignKey('base.Course', related_name='first_course', on_delete=models.CASCADE)
    course2 = models.ForeignKey('base.Course', related_name='second_course', on_delete=models.CASCADE)
    successive = models.BooleanField(verbose_name=_('Successives?'), default=False)
    ND = models.BooleanField(verbose_name=_('On different days'), default=False)

    def __str__(self):
        return f"{self.course1} avant {self.course2}"

    def pre_analysis(self, week):
        #Besoin du nombre de cours de chaque à poser

        possible_tutors_1 = set()
        if self.course1.tutor is not None:
            possible_tutors_1.add(self.course1.tutor)
        elif self.course1.supp_tutor is not None:
            possible_tutors_1.add(self.course1.supp_tutor)
        else:
            return False

        possible_tutors_2 = set()
        if self.course2.tutor is not None:
            possible_tutors_2.add(self.course2.tutor)
        elif self.course2.supp_tutor is not None:
            possible_tutors_2.add(self.course2.supp_tutor)
        else:
            return False


        # Attention, ça ne marche que si TOUS les utilisateurs ont tous mis des prefs de la  semaine
        D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=week, value__gte=1)
        # OU tous mis des prefs que sur la semaine type
        if not D1:
            D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=None, value__gte=1)

        D2 = UserPreference.objects.filter(user__in=possible_tutors_2, week=week, value__gte=1)
        # Attention, ces préférences me permettent-elles d'assurer le course2
        if not D2:
            D2 = UserPreference.objects.filter(user__in=possible_tutors_2, week=None, value__gte=1)
        
        #Si on a des préférences possibles pour les deux
        if D1 and D2:
            if self.successive:
                D1 = [d1 for d1 in D1 for d2 in D2 if d2.is_successor_of(d1)]
                D2 = [d2 for d1 in D1 for d2 in D2 if d2.is_successor_of(d1)]
            elif self.ND:
                #On réduit le nombre de préférences à celles qui ne sont pas le même jour.
                D1 = [d1 for d1 in D1 for d2 in D2 if not d1.same_day(d2)]
                D2 = [d2 for d2 in D2 for d1 in D1 if not d2.same_day(d1)]
                
            #All contradictoire avec same_day ? (voir comparaison des UserPreferences)
            return all([d2 > d1 for d2 in D2 for d1 in D1])
        else:
            #Certains utilisateurs n'ont aucunes préférences de renseignées.
            return False

class Partition(object):
    #date_start, date_end : datetime
    #day_start_time, day_end_time : int
    def __init__(self, type, date_start, date_end, day_start_time, day_end_time):
        self.intervals = []
        self.type = type
        self.day_start_time = day_start_time
        self.day_end_time = day_end_time
        self.intervals.append((TimeInterval(date_start, date_end), []))

    @property
    def day_duration(self):
        return (self.day_end_time - self.day_start_time)

    @property
    def nb_intervals(self):
      return len(self.intervals)

    @property
    def duration(self):
        return abs(self.intervals[len(self.intervals)-1][0].end - self.intervals[0][0].start).total_seconds()//60

    def add_slot(self, interval, data):
        i = 0
        while self.intervals[i][0].end <= interval.start:
            i += 1
        
        while i < len(self.intervals) and interval.end > self.intervals[i][0].start:
            #IF WE ALREADY HAVE THE SAME INTERVAL WE APPEND THE DATA
            if self.intervals[i][0] == interval:
                self.intervals[i][1].append(data.copy())
                i += 1
            #IF WE ARE INSIDE AN EXISTING INTERVAL
            elif self.intervals[i][0].start <= interval.start and self.intervals[i][0].end >= interval.end:
                new_part = 1
                if self.intervals[i][0].end != interval.end:
                    self.intervals.insert(i+1, (TimeInterval(interval.end, self.intervals[i][0].end), self.intervals[i][1].copy()))
                    self.intervals[i][0].end = interval.end
                if self.intervals[i][0].start != interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, interval.end),
                                                self.intervals[i][1][:]+[data.copy()]))
                    new_part += 1
                else:
                    self.intervals[i][1].append(data)
                i += new_part
            #ELSE WE ARE IN BETWEEN TWO INTERVALS
            else:
                self.intervals[i][0].end = interval.start
                self.intervals.insert(i+1, (TimeInterval(interval.start, self.intervals[i+1][0].start),
                                            self.intervals[i][1][:]+[data.copy()]))
                interval.start = self.intervals[i+1][0].end
                i += 2