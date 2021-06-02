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


from django.db import models

from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint
from django.utils.translation import gettext_lazy as _
from base.models import UserPreference
from base.timing import Day, days_list, days_index

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
    #Mettre un start_time des jours, et un end_time des jours ?
    def __init__(self, type, depart, day_start_time, day_end_time, fin = None, start_time = None, end_time = None):
        self.partitions = []
        self.type = type
        self.day_start_time = day_start_time
        self.day_end_time = day_end_time
        self.partitions.append({
                            "day_start" : depart,
                            "data" : { 
                                "free" : True
                            }
                        })
        if fin:
            self.partitions[0]["day_end"] = fin
        else:
            self.partitions[0]["day_end"] = depart
        if start_time:
            self.partitions[0]["start_time"] = start_time
        else:
            self.partitions[0]["start_time"] = self.day_start_time
        
        if end_time:
            self.partitions[0]["end_time"] = end_time
        else:
            self.partitions[0]["end_time"] = self.day_end_time

    @property
    def day_duration(self):
        return self.day_end_time - self.day_start_time

    @property
    def nb_slots(self):
      return len(self.partitions)

    @property
    def duration(self):
        #computes number of minutes for all weeks from the one of day_start to the one of day_end included
        nb_min_weeks = (self.partitions[0]["day_start"].week.nb - self.partitions[self.nb_slots - 1]["day_end"].week.nb + 1) * self.day_duration * 5
        #computes number of minutes from the start of any days to the start of the partition
        nb_min_from_start_day = self.partitions[0]["start_time"] - self.day_start_time
        
        #computes number of minutes from the end of a partition to the end of any days
        nb_min_to_end_day = self.day_end_time - self.partitions[self.nb_slots-1]["end_time"]
        
        #computes number of minutes by days from monday to day_start
        nb_min_from_day_week = self.day_duration * days_index[self.partitions[0]["day_start"].day]

        #computes number of minutes by days from day_end to friday
        nb_min_to_end_week = self.day_duration * (4 - days_index[self.partitions[self.nb_slots-1]["day_end"].day])

        return nb_min_weeks - nb_min_from_start_day - nb_min_to_end_day - nb_min_from_day_week  - nb_min_to_end_week

    def add_slot(self):
        pass
'''
    def get_slot_from_time(self, day, start_time, duration = None):
        i = 0
        if day.week:
            while i < len(self.partitions) and self.partitions[i]["day_start"].week > day.week:
                i+=1
        else:
            return None
        while (i < len(self.partitions)
                and (self.partitions[i]["day_start"].day < day.day
                        and self.partitions[i]["day_start"].day > day.day)
                        ):
            i+=1


        return self.partitions[i]

    def merge_partition(self, other):
      pass

    @classmethod
    def merge_partition(cls, part1, part2):
      pass
'''


'''
class Partition(object):

    operations = {
        #checks if slots have the same tutor 
        "up_tutor" : lambda slot1, slot2 : slot1["data"]["tutor"] == slot2["data"]["tutor"],
        #checks if slots have the same value
        "up_value" : lambda slot1, slot2 : slot1["data"]["value"] == slot2["data"]["value"],
        #checks if slots have the same week
        "up_week" : lambda slot1, slot2 : slot1["data"]["week"] == slot2["data"]["week"],
        #checks if slots types are UserPreference      
        "user_pref": lambda slot1, slot2 : slot1["data"]["type"] == slot2["data"]["type"] == "UserPreference",
        #"no_check" : lambda slot1, slot2 : True,
    }
    courses_break = 20
    def __init__(self, slots = None, week = None):
        self.partitions = {Day.MONDAY: [], Day.TUESDAY: [], Day.WEDNESDAY: [],
                            Day.THURSDAY: [], Day.FRIDAY: [], Day.SATURDAY: [],
                            Day.SUNDAY: []}
        #self.partitions = [[], [], [], [], [], [], []]
                        
        if slots != None:
          if isinstance(slots, list):
            for up in slots:
                if isinstance(up, UserPreference):
                    slot = {
                        "start" : up.start_time,
                        "duration" : up.duration,
                        "data" : { 
                            "type" : "UserPreference",
                            "tutor" : up.user,
                            "value" : up.value,
                            "week" : up.week
                        }
                    }
                    self.partitions[up.day].append(slot)
          elif isinstance(slots, Partition):
              self.partitions = slots.partitions
        self.week = week

    #returns a new instance of Partition with the longest slots in it while checking datas
    #through the "method" function passed as an argument
    def clean(self, methods):
        new_partition = Partition(week=self.week)
        for day, slots in self.partitions.items():
            i = 1
            j = 0
            if slots:
              new_partition.partitions[day].append(slots[0].copy())
              while(i < len(slots)):
                  if (new_partition.partitions[day][j]["start"] +
                          new_partition.partitions[day][j]["duration"] +
                          Partition.courses_break < slots[i]["start"] or
                          not self.all_conditions(slots[i], new_partition.partitions[day][j], methods)):
                      new_partition.partitions[day].append(slots[i].copy())
                      j+=1
                  else:
                      if (new_partition.partitions[day][j]["start"] + new_partition.partitions[day][j]["duration"] + Partition.courses_break 
                          == slots[i]["start"]):
                          new_duration = new_partition.partitions[day][j]["duration"] + slots[i]["duration"] + Partition.courses_break
                      #Pourrait être un else
                      elif new_partition.partitions[day][j]["start"] + new_partition.partitions[day][j]["duration"] + Partition.courses_break > slots[i]["start"]:
                          new_duration = slots[i]["duration"] + slots[i]["start"] - new_partition.partitions[day][j]["start"]
                      new_partition.partitions[day][j]["duration"] = new_duration 
                  i+=1
        return new_partition

    #checks if all conditions are true
    def all_conditions(self, slot1, slot2, methods):
        for method in methods:
            if not Partition.operations[method](slot1, slot2):
                return False
        return True
'''