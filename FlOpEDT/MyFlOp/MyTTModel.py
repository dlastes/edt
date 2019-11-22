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

import importlib
from TTapp.TTModel import TTModel
from TTapp.models import days_filter, Day, slots_filter
from MyFlOp.cosmo_specific_constraints import add_cosmo_specific_constraints
from misc.deploy_database.Files.Cosmo.deploiement import export_scheduled_courses
from base.models import RoomGroup


class MyTTModel(TTModel):
    def __init__(self, department_abbrev, weeks, year,
                 train_prog=None,
                 stabilize_work_copy=None,
                 min_bhd_i=1.,
                 cout_patron_semaine=2.,
                 cout_patron_we=6.
                 ):
        self.nb_heures = {}
        self.cout_patron_semaine = cout_patron_semaine
        self.cout_patron_we = cout_patron_we

        TTModel.__init__(self, department_abbrev, weeks, year,
                         train_prog=train_prog,
                         stabilize_work_copy=stabilize_work_copy,
                         min_bhd_i=min_bhd_i, only_fixed_scheduled_courses=True)
        self.WE, self.WE_3jours, self.quasiWE = self.week_ends_init()
        add_cosmo_specific_constraints(self)

    def week_ends_init(self):
        # Gestion des WE
        WE_3jours = {}
        WE = {}
        quasiWE = {}
        for week in self.wdb.weeks:
            vendredi = days_filter(self.wdb.days, index=4, week=week).pop()
            samedi = days_filter(self.wdb.days, index=5, week=week).pop()
            dimanche = days_filter(self.wdb.days, index=6, week=week).pop()
            if week + 1 in self.wdb.weeks:
                lundi = days_filter(self.wdb.days, index=0, week=week + 1).pop()
            else:
                lundi = 'lundi_fictif'

            for i in self.wdb.instructors:
                WE_3jours[i, week] = self.add_var("%s a son WE de 3 jours semaine %d" % (i, week))
                WE[i, week] = self.add_var("%s a son WE semaine %d" % (i, week))
                quasiWE[i, week] = self.add_var("%s a presque son WE semaine %d" % (i, week))

                #Création d'un IBD à 0 pour le lundi fictif
                if week + 1 not in self.wdb.weeks:
                    self.IBD[i, lundi] = self.add_var("lundi_fictif")
                    self.add_constraint(self.IBD[i, lundi], '==', 1)

                # WE est à 1 si samedi et dimanche à 0
                self.add_constraint(
                    WE[i, week] + self.IBD[i, samedi] + self.IBD[i, dimanche],
                    '>=',
                    1)
                # WE est à 0 si samedi ou dimanche à 1
                self.add_constraint(
                    2 * WE[i, week] + self.IBD[i, samedi] + self.IBD[i, dimanche],
                    '<=',
                    2)

                # WE 3 jours
                self.add_constraint(
                    WE_3jours[i, week] + self.IBD[i, samedi] + self.IBD[i, dimanche] + self.IBD[i, vendredi],
                    '>=',
                    1)
                self.add_constraint(
                    WE_3jours[i, week] + self.IBD[i, samedi] + self.IBD[i, dimanche] + self.IBD[i, lundi],
                    '>=',
                    1)
                self.add_constraint(
                    WE_3jours[i, week] - WE[i, week],
                    '<=',
                    0)
                self.add_constraint(
                    WE_3jours[i, week] + self.IBD[i, vendredi] + self.IBD[i, lundi],
                    '<=',
                    2)

                # quasiWE
                creneaux_du_presque_WE = \
                    self.sum(self.TTinstructors[(sl, c, i)]
                             for sl in
                             slots_filter(self.wdb.slots, week=week, day=vendredi, starts_after=18 * 60)
                             | slots_filter(self.wdb.slots, week=week, day=dimanche, ends_before=17 * 60)
                             | slots_filter(self.wdb.slots, week=week, day=samedi)
                             for c in set(self.wdb.possible_courses[i]) & self.wdb.compatible_courses[sl])

                self.add_constraint(
                    quasiWE[i, week] + creneaux_du_presque_WE,
                    '>=',
                    1)

                self.add_constraint(
                    100 * quasiWE[i, week] + creneaux_du_presque_WE,
                    '<=',
                    100)
        return WE, WE_3jours, quasiWE


    def add_specific_constraints(self):
        """
        The speficic constraints stored in the database are added by the
        TTModel class.
        If you shall add more specific ones, you may write it down here.
        """
        TTModel.add_specific_constraints(self)

    def compute_non_prefered_slot_cost(self):
        avail_instr, unp_slot_cost = TTModel.compute_non_prefered_slot_cost(self)
        patrons = {'Annie', 'Jeremy'}
        for i in self.wdb.instructors:
            if i.username in patrons:
                for sl in unp_slot_cost[i]:
                    if sl.day.day in [Day.SATURDAY, Day.SUNDAY]:
                        unp_slot_cost[i][sl] += self.cout_patron_we
                    else:
                        unp_slot_cost[i][sl] += self.cout_patron_semaine
        self.add_warning(None, "Les créneaux des patrons coutent %d de plus, et %d le WE" % (self.cout_patron_semaine,
                                                                                             self.cout_patron_we))
        return avail_instr, unp_slot_cost

    def add_rooms_constraints(self):
        print("adding room constraints")
        for rg in RoomGroup.objects.all():
            for s_c in self.wdb.sched_courses.filter(cours__module__abbrev=rg.name):
                c = s_c.cours
                for sl in self.wdb.compatible_slots[c]:
                    name = 'core_roomtype_' + str(rg) + '_' + str(sl)
                    self.add_constraint(self.TTrooms[(sl, c, rg)] - self.TT[(sl, c)],
                                        '==',
                                        0,
                                        name)

    def solve(self, time_limit=3600, target_work_copy=None,
              solver='gurobi'):
        """
        If you shall add pre (or post) processing apps, you may write them down
        here.
        """
        work_copy = TTModel.solve(self,
                                  time_limit=time_limit,
                                  target_work_copy=target_work_copy,
                                  solver=solver)
        if work_copy is not None:
            retour = {i.username: {} for i in self.nb_heures}
            for i in self.nb_heures:
                retour[i.username] = {week: {'WE': 0, 'heures': {}} for week in ['total'] + self.wdb.weeks}
                retour[i.username]['total']['heures'] = 0
                for week in self.wdb.weeks:
                    retour[i.username][week]['heures']['total'] = self.get_expr_value(self.nb_heures[i][week])
                    retour[i.username]['total']['heures'] += self.get_expr_value(self.nb_heures[i][week])
                    if self.get_expr_value(self.WE_3jours[i, week]) != 0:
                        retour[i.username][week]['WE'] = 3
                    elif self.get_expr_value(self.WE[i, week]) != 0:
                        retour[i.username][week]['WE'] = 2
                    elif self.get_expr_value(self.quasiWE[i, week]) != 0:
                        retour[i.username][week]['WE'] = 1
                    retour[i.username]['total']['WE'] += retour[i.username][week]['WE']

                    for day in days_filter(self.wdb.days, week=week):
                        if self.get_expr_value(self.nb_heures[i][day]) != 0:
                            retour[i.username][week]['heures'][day.day] = self.get_expr_value(self.nb_heures[i][day])
            print(retour)
            book = export_scheduled_courses(self.wdb.weeks, work_copy=work_copy)
            book.create_sheet('Analyse')
            analyse = book['Analyse']
            analyse['A1'] = "Salarié"
            col = 3
            semaines = self.wdb.weeks
            for week in semaines:
                a = analyse.cell(row=1, column=col)
                a.value = str(week)
                col += 1
            row = 2
            for salarie in retour:
                a = analyse.cell(row=row, column=1)
                a.value = salarie
                a = analyse.cell(row=row, column=2)
                a.value = 'Heures'
                a = analyse.cell(row=row+1, column=2)
                a.value = 'WE'
                col = 3
                for week in semaines:
                    a = analyse.cell(row=row, column=col)
                    a.value = retour[salarie][week]['heures']['total']
                    a = analyse.cell(row=row+1, column=col)
                    a.value = retour[salarie][week]['WE']
                    col += 1
                row += 3
            book.save("misc/deploy_database/Files/Cosmo/Cosmo-plannings-generes-semaines-%g-a-%g_#%g.xlsx"
                      % (semaines[0], semaines[-1], work_copy))
            return retour

        if work_copy is None:
            spec = importlib.util.find_spec('gurobipy')
            if spec:
                from gurobipy import read
                lp = "FlOpTT-pulp.lp"
                m = read(lp)
                # m.optimize()
                m.computeIIS()
                m.write("logs/IIS_week%s.ilp" % self.weeks)
                print("IIS written in file logs/IIS_week%s.ilp" % (self.weeks))

