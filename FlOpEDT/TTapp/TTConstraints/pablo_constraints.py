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

from TTapp.TTconstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint


class LowerBoundBusyDays(TTConstraint):
    """
    Commentaire à écrire
    """
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    min_days_nb = models.PositiveSmallIntegerField()
    lower_bound_hours = models.PositiveSmallIntegerField()

    def enrich_model(self, ttmodel, week, ponderation=1):
        relevant_courses = self.get_courses_queryset_by_attributes(ttmodel, week)

        if sum(c.type.duration for c in relevant_courses) > self.lower_bound_hours:
            ttmodel.add_constraint(ttmodel.IBD_GTE[self.min_days_nb][self.tutor], '==', 1,
                                   Constraint(constraint_type='LowerBoundBusyDays', instructors=self.tutor))

    def one_line_description(self):
        return f"Si plus de {self.lower_bound_hours} heures pour {self.tutor}  alors au moins {self.min_days_nb} jours"