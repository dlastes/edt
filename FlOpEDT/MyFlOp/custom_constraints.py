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

import TTapp.constraint_type as ct
from TTapp.models import days_filter, slots_filter

# class DummyConstraintTemplate():
#     """
#     This class is a template for writing your own custom contraint. 

#     The module can contains several custom constraints.
#     """

#     def enrich_model(self, ttmodel, ponderation, **kwargs):
#         """
#         You can enrich ttmodel here with your specific constraints
#         and variables
#         """
#         pass

    
#     def get_viewmodel(self):
#         """
#         You can add one or more details to be displayed in the solve board 
#         interface about what this constraint does
#         """
#         return {'detail_name_sample': "detail_content_sample", }


#     def one_line_description(self):
#         """
#         You can give a contextual explanation about what this constraint doesnt
#         """
#         return "DummyConstraint online description"

# TO BE IMPROVED!!!
def define_attributes(ttmodel, kwargs):
    if 'weeks' in kwargs:
        weeks = [week for week in ttmodel.weeks if week in kwargs["weeks"]]
    else:
        weeks = ttmodel.weeks
    if 'tutors' in kwargs:
        tutors = set(t for t in ttmodel.wdb.instructors if t in kwargs["tutors"])
    else:
        tutors = set(ttmodel.wdb.instructors)
    if 'groups' in kwargs:
        groups = set(g for g in ttmodel.wdb.groups if g in kwargs["groups"])
    else:
        groups = set(ttmodel.wdb.basic_groups)
    return weeks, tutors, groups


class MinimizeBusyDays:
    """
    This class is a template for writing your own custom contraint.

    The module can contains several custom constraints.
    """

    def enrich_model(self, ttmodel, ponderation, **kwargs):
        """
        Minimize the number of busy days for tutor with cost
        (if it does not overcome the bound expressed in pref_hours_per_day)
        """
        weeks, tutors, groups = define_attributes(ttmodel, kwargs)
        for week in weeks:
            for tutor in tutors:
                slot_by_day_cost = 0
                # need to be sorted
                courses_hours = sum(c.type.duration
                                    for c in (ttmodel.wdb.courses_for_tutor[tutor]
                                              | ttmodel.wdb.courses_for_supp_tutor[tutor])
                                    & ttmodel.wdb.courses_by_week[week]) \
                                / 60
                nb_days = 5
                frontier_pref_busy_days = [tutor.pref_hours_per_day * d for d in range(nb_days - 1, 0, -1)]

                for fr in frontier_pref_busy_days:
                    if courses_hours <= fr:
                        slot_by_day_cost *= 2
                        slot_by_day_cost += ttmodel.IBD_GTE[week][nb_days][tutor]
                        nb_days -= 1
                    else:
                        break
                ttmodel.add_to_inst_cost(tutor, ttmodel.min_bd_i * slot_by_day_cost, week=week)

    def get_viewmodel(self):
        """
        You can add one or more details to be displayed in the solve board
        interface about what this constraint does
        """
        return {'detail_name_sample': "detail_content_sample", }

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "MinimizeBusyDays online description"

    class Meta:
        verbose_name = "Minimiser les jours de présence"


class RespectBoundPerDay:
    """
    This class is a template for writing your own custom contraint.

    The module can contains several custom constraints.
    """

    def enrich_model(self, ttmodel, ponderation, **kwargs):
        """
        Minimize the number of busy days for tutor with cost
        (if it does not overcome the bound expressed in pref_hours_per_day)
        """
        weeks, tutors, groups = define_attributes(ttmodel, kwargs)
        for week in weeks:
            for tutor in tutors:
                for d in days_filter(ttmodel.wdb.days, week=week):
                    ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] * c.type.duration / 60
                                                       for c in ttmodel.wdb.courses_for_tutor[tutor] if c.week == week
                                                       for sl in slots_filter(ttmodel.wdb.slots, day=d)
                                                       & ttmodel.wdb.compatible_slots[c]),
                                           '<=',
                                           tutor.max_hours_per_day,
                                           constraint_type=ct.ConstraintType.BOUND_HOURS_PER_DAY, instructors=tutor,
                                           days=d)

    def get_viewmodel(self):
        """
        You can add one or more details to be displayed in the solve board
        interface about what this constraint does
        """
        return {'detail_name_sample': "detail_content_sample", }

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "RespectBoundPerDay online description"

    class Meta:
        verbose_name = "Respecter les limites horaires"
