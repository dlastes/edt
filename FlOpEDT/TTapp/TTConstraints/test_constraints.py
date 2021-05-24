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
        nb_required_1 = 1
        nb_required_2 = 1

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
                
            #Of récupère le nombre de possibilitées
            nb_possible_1 = len(D1)
            nb_possible_2 = len(D2)

            #All contradictoire avec same_day ? (voir comparaison des UserPreferences)
            return all([d2 > d1 for d2 in D2 for d1 in D1]
                    and nb_possible_1 > nb_required_1 and nb_possible_2 > nb_required_2)
        else:
            #Certains utilisateurs n'ont aucunes préférences de renseignées.
            return False