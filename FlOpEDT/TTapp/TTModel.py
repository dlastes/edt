#!/usr/bin/env python2
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


# ### Have to do this for it to work in 1.9.x!
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

from pulp import LpVariable, LpConstraint, LpBinary, LpConstraintEQ, LpConstraintGE, LpConstraintLE, \
    LpAffineExpression, LpProblem, LpStatus, LpMinimize, lpSum

from pulp import GUROBI_CMD, PULP_CBC_CMD

import modif.models as db

from modif.weeks import annee_courante

from TTapp.models import MinNonPreferedSlot, max_weight, Stabilize, TTConstraint

import os

from MyFlOp.MyTTUtils import reassign_rooms

import signal

from django.db.models import Q, Max

import datetime


# import os, glob


class WeekDB(object):
    def __init__(self, semaine, an, promo=[1, 2, 3]):
        self.slots = db.Creneau.objects.all()
        self.week = semaine
        self.year = an
        self.groups = db.Groupe.objects.filter(promo__in=promo)
        self.days = db.Jour.objects.all()
        self.rooms = db.Room.objects.all()
        self.room_groups = db.RoomGroup.objects.all()
        self.room_types = db.RoomType.objects.all()
        self.room_prefs = db.RoomPreference.objects.all()
        self.room_groups_for_type = {}
        for t in self.room_types:
            self.room_groups_for_type[t] = db.RoomGroup.objects.filter(types=t)
        self.courses = db.Cours.objects.filter(semaine=semaine, an=an, groupe__promo__in=promo)
        self.basic_groups = self.groups \
            .filter(basic=True,
                    id__in=self.courses
                    .values_list('groupe_id')
                    .distinct())
        self.basic_groups_surgroups = {}
        for g in self.basic_groups:
            self.basic_groups_surgroups[g] = [g] + g.surgroupes()
        self.courses_for_group = {}
        for g in self.groups:
            self.courses_for_group[g] = self.courses.filter(groupe=g)

        self.availabilities = db.Disponibilite.objects \
            .filter(semaine=semaine,
                    an=an)
        self.instructors = db.Prof.objects \
            .filter(id__in=self.courses
                    .values_list('prof_id')
                    .distinct())
        self.sched_courses = db.CoursPlace \
            .objects \
            .filter(cours__semaine=semaine,
                    cours__an=an,
                    cours__groupe__promo__in=promo)
        self.fixed_courses = db.CoursPlace.objects.filter(cours__semaine=semaine, cours__an=an,
                                                          copie_travail=0) \
            .exclude(cours__groupe__promo__in=promo)

        self.courses_availabilities = db.DispoCours.objects \
            .filter(semaine=semaine,
                    an=an)
        self.modules = db.Module.objects \
            .filter(id__in=self.courses
                    .values_list('module_id')
                    .distinct())
        self.PVHDs = db.DemiJourFeriePromo.objects.filter(semaine=semaine,
                                                          an=an)
        self.Precede = db.Precede.objects.filter(cours1__semaine=semaine,
                                                 cours2__semaine=semaine,
                                                 cours1__groupe__promo__in=promo)
        self.courses_for_prof = {}
        for i in self.instructors:
            self.courses_for_prof[i] = self.courses.filter(prof=i)
        self.courses_for_profsupp = {}
        for i in self.instructors:
            self.courses_for_profsupp[i] = self.courses.filter(profsupp=i)


class TTModel(object):
    def __init__(self, semaine, an,
                 promo=[1, 2, 3],
                 stabilize_work_copy=None,
                 min_nps_i=1.,
                 min_bhd_g=1.,
                 min_bd_i=1.,
                 min_bhd_i=1.,
                 min_nps_c=1.,
                 max_stab=5.,
                 lim_ld=1.):
        print "\nLet's start week #%g" % semaine
        self.model = LpProblem("FlOpTT", LpMinimize)
        self.min_ups_i = min_nps_i
        self.min_bhd_g = min_bhd_g
        self.min_bd_i = min_bd_i
        self.min_bhd_i = min_bhd_i
        self.min_ups_c = min_nps_c
        self.max_stab = max_stab
        self.lim_ld = lim_ld
        self.var_nb = 0
        self.semaine = semaine
        self.an = an
        if type(promo) is int:
            self.promo=[promo]
        else:
            self.promo = promo
        self.stabilize_work_copy = stabilize_work_copy
        self.wdb = WeekDB(semaine, an, promo)
        self.obj = self.lin_expr()
        self.cost_I = dict(zip(self.wdb.instructors, [self.lin_expr() for _ in self.wdb.instructors]))
        self.FHD_G = {}
        for apm in [db.Heure.MATIN, db.Heure.APREM]:
            self.FHD_G[apm] = dict(zip(self.wdb.basic_groups, [self.lin_expr() for _ in self.wdb.basic_groups]))
        self.cost_SL = dict(zip(self.wdb.slots, [self.lin_expr() for _ in self.wdb.slots]))
        self.cost_G = dict(zip(self.wdb.basic_groups, [self.lin_expr() for _ in self.wdb.basic_groups]))
        self.TT = {}
        self.TTrooms = {}
        for sl in self.wdb.slots:
            for c in self.wdb.courses:
                # print c, c.room_type
                self.TT[(sl, c)] = self.add_var("TT(%s,%s)" % (sl, c))
                for rg in self.wdb.room_groups_for_type[c.room_type]:
                    self.TTrooms[(sl, c, rg)] = self.add_var("TTroom(%s,%s,%s)" % (sl, c, rg))

        self.IBD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                self.IBD[(i, d)] = self.add_var("IBD(%s,%s)" % (i, d))
                # Linking the variable to the TT
                dayslots = self.wdb.slots.filter(jour=d)
                card = 2 * len(dayslots)
                expr = self.lin_expr()
                expr += card * self.IBD[(i, d)]
                for c in self.wdb.courses_for_prof[i]:
                    for sl in dayslots:
                        expr -= self.TT[(sl, c)]
                self.add_constraint(expr, '>=', 0)

                if self.wdb.fixed_courses.filter(cours__prof=i, creneau__jour=d):
                    self.add_constraint(self.IBD[(i, d)], '==', 1)
                    # This next constraint impides to force IBD to be 1 (if there is a meeting, for example...)
                    # self.add_constraint(expr, '<=', card-1)

        self.IBD_GTE = []
        max_days = 5
        for j in range(max_days + 1):
            self.IBD_GTE.append({})

        for i in self.wdb.instructors:
            for j in range(2, max_days + 1):
                self.IBD_GTE[j][i] = \
                    self.add_floor(str(i) + str(j),
                                   self.sum(self.IBD[(i, d)] for d in self.wdb.days), j, max_days)

        self.IBHD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                self.IBHD[(i, d, 'AM')] = self.add_var("IBHD(%s,%s,%s)" % (i, d, 'AM'))
                self.IBHD[(i, d, 'PM')] = self.add_var("IBHD(%s,%s,%s)" % (i, d, 'PM'))
                # add constraint linking IBHD to TT
                for apm in ['AM', 'PM']:
                    halfdayslots = self.wdb.slots.filter(jour=d, heure__apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * self.IBHD[(i, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.courses_for_prof[i]:
                            expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0)
                    # This constraint impides to force IBHD to be 1
                    # (if there is a meeting, for example...)
                    if self.wdb.fixed_courses.filter(cours__prof=i, creneau__jour=d, creneau__heure__apm=apm):
                        self.add_constraint(self.IBHD[(i, d, apm)], '==', 1)
                    else:
                        self.add_constraint(expr, '<=', card - 1)

        self.GBHD = {}
        for g in self.wdb.basic_groups:
            for d in self.wdb.days:
                self.GBHD[(g, d, 'AM')] = self.add_var("GBHD(%s,%s,%s)" % (g, d, 'AM'))
                self.GBHD[(g, d, 'PM')] = self.add_var("GBHD(%s,%s,%s)" % (g, d, 'PM'))
                # add constraint linking IBD to EDT
                for apm in [db.Heure.MATIN, db.Heure.APREM]:
                    halfdayslots = self.wdb.slots.filter(jour=d, heure__apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * self.GBHD[(g, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.courses_for_group[g]:
                            expr -= self.TT[(sl, c)]
                        for sg in g.surgroupes():
                            for c in self.wdb.courses_for_group[sg]:
                                expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0)
                    self.add_constraint(expr, '<=', card - 1)

        self.avail_instr, self.unp_slot_cost = self.compute_non_prefered_slot_cost()

        self.unp_slot_cost_course, self.avail_course \
            = self.compute_non_prefered_slot_cost_course()

        for i in self.wdb.instructors:
            for sl in self.wdb.slots:
                if sl not in self.avail_instr[i]:
                    self.avail_instr[i][sl] = 0
                if sl not in self.unp_slot_cost[i]:
                    self.unp_slot_cost[i][sl] = 0

        self.add_TT_constraints()

        self.update_objective()

    def add_var(self, name):
        """
        Create a PuLP binary variable
        """
        # return LpVariable(name, lowBound = 0, upBound = 1, cat = LpBinary)
        countedname = name + '_' + str(self.var_nb)
        self.var_nb += 1
        return LpVariable(countedname, cat=LpBinary)

    def add_constraint(self, expr, relation, value, name=None):
        """
        Add a constraint to the model
        """
        if relation == '==':
            pulp_relation = LpConstraintEQ
        elif relation == '<=':
            pulp_relation = LpConstraintLE
        elif relation == '>=':
            pulp_relation = LpConstraintGE
        else:
            raise Exception("relation must be either '==' or '>=' or '<='")

        self.model += LpConstraint(e=expr, sense=pulp_relation, rhs=value, name=name)

    def lin_expr(self, expr=None):
        return LpAffineExpression(expr)

    def sum(self, *args):
        return lpSum(list(*args))

    def get_var_value(self, ttvar):
        return round(ttvar.value())

    def get_expr_value(self, ttexpr):
        return ttexpr.value()

    def get_obj_coeffs(self):
        """
        get the coeff of each var in the objective
        """
        l = [(weight, var) for (var, weight) in self.obj.iteritems() if var.value() != 0 and round(weight) != 0]
        l.sort(reverse=True)
        return l

    def set_objective(self, obj):
        self.model.setObjective(obj)

    def get_constraint(self, name):
        return self.model.constraints[name]

    def get_all_constraints(self):
        return self.model.constraints

    def remove_constraint(self, constraint_name):
        del self.model.constraints[constraint_name]

    def var_coeff(self, var, constraint):
        return constraint[var]

    def change_var_coeff(self, var, constraint, newvalue):
        constraint[var] = newvalue

    def add_conjunct(self, v1, v2):
        """
        Crée une nouvelle variable qui est la conjonction des deux et l'ajoute au modèle
        """
        l_conj_var = self.add_var("%s*%s" % (str(v1), str(v2)))
        self.add_constraint(l_conj_var - (v1 + v2), '>=', -1)
        self.add_constraint(l_conj_var - ((v1 + v2) / 2), '<=', 0)
        return l_conj_var

    def add_floor(self, name, expr, floor, bound):
        """
        Add a variable that equals 1 if expr >= floor, is integer expr is known to be within [0, bound]
        """
        l_floor = self.add_var("FLOOR %s %d" % (name, floor))
        self.add_constraint(expr - l_floor * floor, '>=', 0)
        self.add_constraint(l_floor * bound - expr, '>=', 1 - floor)
        return l_floor

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost):
        self.cost_I[instructor] += cost

    def add_to_group_cost(self, group, cost):
        self.cost_G[group] += cost

    def add_stabilization_constraints(self):
        if len(self.promo) < 3:
            print 'Will modify only courses of promo(s)', self.promo

        # maximize stability
        if self.stabilize_work_copy is not None:
            Stabilize(general=True,
                      work_copy=self.stabilize_work_copy) \
                .enrich_model(self, self.max_stab)
            print 'Will stabilize from remote work copy #', self.stabilize_work_copy
        else:
            print 'No stabilization'

    def add_core_constraints(self):
        """
        Add the core constraints to the PuLP model :
            - a course is scheduled once and only once
            - no group has two courses in parallel
            - + a teacher does not have 2 courses in parallel
              + the teachers are available on the chosen slots
            - no course on vacation days
        """

        print "adding core constraints"
        for c in self.wdb.courses:
            name = 'core_course_' + str(c) + "_" + str(c.id)
            self.add_constraint(self.sum([self.TT[(sl, c)] for sl in self.wdb.slots]), '==', 1, name=name)

        for sl in self.wdb.slots:
            for g in self.wdb.basic_groups:
                expr = self.lin_expr()
                for sg in self.wdb.basic_groups_surgroups[g]:
                    for c in self.wdb.courses_for_group[sg]:
                        expr += self.TT[(sl, c)]
                name = 'core_group_' + str(g) + '_' + str(sl)
                self.add_constraint(expr, '<=', 1, name=name)

        for sl in self.wdb.slots:
            for i in self.wdb.instructors:
                if self.wdb.fixed_courses.filter(cours__prof=i, creneau=sl):
                    name = 'fixed_course_prof_' + str(i) + '_' + str(sl)
                    instr_courses = self.wdb.courses_for_prof[i]
                    self.add_constraint(self.sum(self.TT[(sl, c)] for c in instr_courses), '==', 0, name=name)
                else:
                    expr = self.lin_expr()
                    for c in self.wdb.courses_for_prof[i]:
                        expr += self.TT[(sl, c)]
                    for c in self.wdb.courses_for_profsupp[i]:
                        expr += self.TT[(sl, c)]
                    name = 'core_prof_' + str(i) + '_' + str(sl)
                    self.add_constraint(expr, '<=', self.avail_instr[i][sl], name=name)

        # Promo Vacation Half Days (TO BE CHANGED!)
        for PVHD in self.wdb.PVHDs:
            for sl in self.wdb.slots.filter(jour=PVHD.jour,
                                            heure__apm=PVHD.apm):
                for c in self.wdb.courses.filter(groupe__promo=PVHD.promo):
                    self.add_constraint(self.TT[(sl, c)], '==', 0)

    def add_rooms_constraints(self):
        print "adding room constraints"
        # constraint Rooms : there are enough rooms of each type for each slot
        # for each Room, first build the list of courses that may use it
        room_course_compat = {}
        for r in self.wdb.rooms:
            # print "compat for ", r
            room_course_compat[r] = []
            for rg in r.subroom_of.all():
                room_course_compat[r].extend([(c, rg) for c in
                                              self.wdb.courses.filter(room_type__in=rg.types.all())])

        course_rg_compat = {}
        for c in self.wdb.courses:
            course_rg_compat[c] = c.room_type.members.all()

        for sl in self.wdb.slots:
            # print '***', sl
            # constraint : each course is assigned to a RoomGroup
            for c in self.wdb.courses:
                # if sl == self.wdb.slots[0]:
                #     print "C", c, quicksum(self.TTrooms[(sl, c, rg)] for rg in course_rg_compat[c]) == self.TT[
                #         (sl, c)]
                self.add_constraint(
                    self.sum(self.TTrooms[(sl, c, rg)] for rg in course_rg_compat[c]) - self.TT[(sl, c)], '==', 0)
            # constraint : each Room is only used once and only when available
            for r in self.wdb.rooms:
                # if sl == self.wdb.slots[0]:
                #     print "R", r, quicksum(self.TTrooms[(sl, c, rg)] for (c, rg) in room_course_compat[r])
                limit = 1 - len(
                    db.RoomUnavailability.objects.filter(semaine=self.semaine, an=self.an, creneau=sl, room=r))
                # print "limit=",limit,".",
                self.add_constraint(self.sum(self.TTrooms[(sl, c, rg)] for (c, rg) in room_course_compat[r]),
                                    '<=', limit, name='core_room_' + str(r) + '_' + str(sl))
            # constraint : respect preference order, if preferred room is available
            for rp in self.wdb.room_prefs:
                e = self.sum(self.TTrooms[(sl, c, rp.unprefer)] for c in self.wdb.courses.filter(room_type=rp.for_type))
                preferred_is_unavailable = False
                for r in rp.prefer.subrooms.all():
                    if len(db.RoomUnavailability.objects.filter(semaine=self.semaine, an=self.an, creneau=sl,
                                                                room=r)) > 0:
                        # print r, "unavailable for ",sl
                        preferred_is_unavailable = True
                        break
                    e -= self.sum(self.TTrooms[(sl, c, rg)] for (c, rg) in room_course_compat[r])
                if preferred_is_unavailable:
                    continue
                # print "### slot :", sl, rp.unprefer, "after", rp.prefer
                # print e <= 0
                self.add_constraint(
                    e,
                    '<=',
                    0
                )

                # constraint : respect preference order with full order for each room type : perfs OK
                # for rt in self.wdb.room_types:
                #     l=[]
                #     for rgp in rt.members.all():
                #         if len(l)>0:
                #             for rgp_before in l:
                #                 e = quicksum(self.TTrooms[(sl, c, rgp)]
                #                              for c in self.wdb.courses.filter(room_type=rt))
                #                 preferred_is_unavailable = False
                #                 for r in rgp_before.subrooms.all():
                #                     if len(db.RoomUnavailability.objects.filter(semaine=self.semaine, an=self.an,
                #                                                                 creneau=sl, room=r)) > 0:
                #                         # print r, "unavailable for ",sl
                #                         preferred_is_unavailable = True
                #                         break
                #                     e -= quicksum(self.TTrooms[(sl, c, rg)] for (c, rg) in room_course_compat[r])
                #                 if preferred_is_unavailable:
                #                     continue
                #                 self.add_constraint(
                #                     e,
                #                     GRB.LESS_EQUAL,
                #                     0
                #                 )
                #         l.append(rgp)

    def add_precedence_constraints(self, weight=None):
        """
        Add the constraints of precedence saved on the DB:
        -include successivity
        -include non same-day constraint
        -include simultaneity (double precedence)
        If there is a weight, it's a preference, else it's a constraint...
        """
        print 'adding precedence constraints'
        for p in self.wdb.Precede:
            c1 = p.cours1
            c2 = p.cours2
            for sl1 in self.wdb.slots:
                for sl2 in self.wdb.slots:
                    if (p.ND and (sl2.jour == sl1.jour)) \
                            or (p.successifs and (sl2.heure.no != sl1.heure.no + 1 or sl2.jour != sl1.jour)) \
                            or (sl2.jour.no < sl1.jour.no or (sl2.jour == sl1.jour and sl2.heure.no < sl1.heure.no)):
                        if not weight:
                            self.add_constraint(self.TT[(sl1, c1)] + self.TT[(sl2, c2)], '<=', 1)
                        else:
                            conj_var = self.add_conjunct(self.TT[(sl1, c1)], self.TT[(sl2, c2)])
                            self.obj += conj_var * weight

    def compute_non_prefered_slot_cost(self):
        """
        Returns:
            - UnpSlotCost : a 2 level-dictionary { teacher => slot => cost (float in [0,1])}}
            - availInstr : a 2 level-dictionary { teacher => slot => 0/1 }

        The slot cost will be:
            - 0 if it is a prefered slot
            - max(0., 2 - slot value / (average of slot values) )
        """

        avail_instr = {}
        unp_slot_cost = {}
        # dict(zip(instructors, [dict(zip(mm.disponibilite.objects.filter(),[for sl in ])) for i in instructors]))
        # unpreferred slots for an instructor costs min((float(nb_avail_slots) / min(2*nb_teaching_slots,22)),1)
        for i in self.wdb.instructors:
            nb_teaching_slots = len(self.wdb.courses_for_prof[i])
            avail_instr[i] = {}
            unp_slot_cost[i] = {}
            if self.wdb.availabilities.filter(prof=i):
                availabilities = self.wdb.availabilities.filter(prof=i)
            else:
                availabilities = db.Disponibilite \
                    .objects \
                    .filter(prof=i,
                            semaine=None,
                            an=annee_courante)

            if not availabilities:
                print "%s has given no availability information !" % i.user.username
                for slot in self.wdb.slots:
                    unp_slot_cost[i][slot] = 0
                    avail_instr[i][slot] = 1

            else:
                nb_avail_slots = len(availabilities.filter(valeur__gte=1))
                maximum = max([a.valeur for a in availabilities])
                nb_non_prefered_slots = len(availabilities.filter(valeur__gte=1,
                                                                  valeur__lte=maximum - 1))

                if nb_avail_slots < nb_teaching_slots:
                    print "%s has given %g available slots for %g courses... Every slot is considered available !" % (
                        i.user.username, nb_avail_slots, nb_teaching_slots)
                    for a in availabilities:
                        avail_instr[i][a.creneau] = 1
                        if a.valeur >= 1:
                            unp_slot_cost[i][a.creneau] = 0
                        else:
                            unp_slot_cost[i][a.creneau] = 1

                            # TROP TORDU A AMELIORER --> JOURS FERIES POUR DE VRAI!
                elif (
                            (self.wdb.week == 14) and all(
                                x.creneau.jour.no == 0 for x in availabilities.filter(valeur__gte=1))) \
                        or ((self.wdb.week == 18) and all(
                                x.creneau.jour.no == 1 for x in availabilities.filter(valeur__gte=1))) \
                        or ((self.wdb.week == 19) and all(
                                x.creneau.jour.no in [1, 3, 4] for x in availabilities.filter(valeur__gte=1))) \
                        or ((self.wdb.week == 21) and all(
                            x.creneau.jour.no == 0 for x in availabilities.filter(valeur__gte=1))):
                    print "%s has given availabilities only on vacation days!" % i.user.username
                    for a in availabilities:
                        avail_instr[i][a.creneau] = 1
                        if a.valeur >= 1:
                            unp_slot_cost[i][a.creneau] = 0
                        else:
                            unp_slot_cost[i][a.creneau] = 1

                else:
                    moyenne = 0.
                    for a in availabilities:
                        if a.valeur == 0:
                            avail_instr[i][a.creneau] = 0
                        elif a.valeur == maximum:
                            avail_instr[i][a.creneau] = 1
                        else:
                            avail_instr[i][a.creneau] = 1
                            moyenne += a.valeur
                    if nb_non_prefered_slots == 0:
                        moyenne = 1.0 * maximum
                    else:
                        moyenne /= nb_non_prefered_slots

                    if nb_teaching_slots < 9 \
                            and nb_avail_slots < 2 * nb_teaching_slots:
                        print "%s: only %g available slots dispos for %g courses..." % (
                            i.user.username, nb_avail_slots, nb_teaching_slots)
                        for a in availabilities:
                            unp_slot_cost[i][a.creneau] = 0
                    else:
                        for a in availabilities:
                            if a.valeur == maximum or a.valeur == 0:
                                unp_slot_cost[i][a.creneau] = 0
                            else:
                                unp_slot_cost[i][a.creneau] = \
                                    max(0., 2 - a.valeur / moyenne)

        return avail_instr, unp_slot_cost

    def compute_non_prefered_slot_cost_course(self):
        """
         il renvoie:
         non_prefered_slot_cost_course : a dict { Type de cours => { créneau non préféré => cout (float in [0,1])}}
         avail_course : a 2 level-dictionary { Type de cours => slot => 0/1 }
        """

        non_prefered_slot_cost_course = {}
        avail_course = {}
        for nature in [db.Cours.TP, db.Cours.TD, db.Cours.DS, db.Cours.CM]:
            for promo in [1, 2, 3]:
                avail_course[(nature, promo)] = {}
                non_prefered_slot_cost_course[(nature, promo)] = {}
                courses_avail = self.wdb \
                    .courses_availabilities \
                    .filter(nature=nature, promo=promo)
                if not courses_avail:
                    courses_avail = db.DispoCours.objects \
                        .filter(nature=nature,
                                promo=promo,
                                semaine=None,
                                an=annee_courante)
                for sl in self.wdb.slots:
                    try:
                        a = courses_avail.get(creneau=sl)
                    except:
                        print "Course availability problem for %s - promo%g on slot %s" % (nature, promo, sl)
                    if a.valeur == 0:
                        avail_course[(nature, promo)][a.creneau] = 0
                        non_prefered_slot_cost_course[(nature, promo)][a.creneau] = 5
                    else:
                        avail_course[(nature, promo)][a.creneau] = 1
                        non_prefered_slot_cost_course[(nature, promo)][a.creneau] \
                            = 1 - float(a.valeur) / 10

        return non_prefered_slot_cost_course, avail_course

    def add_tt_to_db(self, target_work_copy):
        for sl in self.wdb.slots:
            for c in self.wdb.courses:
                if self.get_var_value(self.TT[(sl, c)]) == 1:
                    # No = len(self.wdb.sched_courses \
                    #          .filter(cours__module=c.module,
                    #                  cours__groupe=c.groupe,
                    #                  cours__semaine__lte=self.semaine - 1,
                    #                  copie_travail=0))
                    # No += len(db.CoursPlace.objects \
                    #           .filter(cours__module=c.module,
                    #                   cours__groupe=c.groupe,
                    #                   cours__semaine=self.semaine,
                    #                   copie_travail=target_work_copy))
                    cp = db.CoursPlace(cours=c,
                                       creneau=sl,
                                       copie_travail=target_work_copy)
                    for rg in c.room_type.members.all():
                        if self.get_var_value(self.TTrooms[(sl, c, rg)]) == 1:
                            cp.room = rg
                    cp.save()
        for fc in self.wdb.fixed_courses:
            cp = db.CoursPlace(cours=fc.cours,
                               creneau=fc.creneau,
                               room=fc.room,
                               copie_travail=target_work_copy)
            cp.save()

        # On enregistre les coûts dans la BDD
        db.CoutProf.objects.filter(semaine=self.wdb.week, an=self.wdb.year).delete()
        db.DJLGroupe.objects.filter(semaine=self.wdb.week, an=self.wdb.year).delete()
        db.CoutGroupe.objects.filter(semaine=self.wdb.week, an=self.wdb.year).delete()

        for i in self.wdb.instructors:
            cp = db.CoutProf(prof=i, an=self.wdb.year, semaine=self.wdb.week,
                             valeur=self.get_expr_value(self.cost_I[i]))
            cp.save()

        for g in self.wdb.basic_groups:
            djlg = db.DJLGroupe(groupe=g, an=self.wdb.year, semaine=self.wdb.week,
                                DJL=self.get_expr_value(self.FHD_G['PM'][g]) +
                                0.5 * self.get_expr_value(self.FHD_G['AM'][g]))
            djlg.save()
            cg = db.CoutGroupe(groupe=g, an=self.wdb.year, semaine=self.wdb.week,
                               valeur=self.get_expr_value(self.cost_G[g]))
            cg.save()

    def add_slot_preferences(self):
        print "adding slot preferences"
        # first objective  => minimise use of unpreferred slots for teachers
        # ponderation MIN_UPS_I
        for i in self.wdb.instructors:
            MinNonPreferedSlot(prof=i,
                               weight=max_weight) \
                .enrich_model(self,
                              ponderation=self.min_ups_i)

        # second objective  => minimise use of unpreferred slots for courses
        # ponderation MIN_UPS_C
        for promo in [1, 2, 3]:
            MinNonPreferedSlot(promo=promo,
                               weight=max_weight) \
                .enrich_model(self,
                              ponderation=self.min_ups_c)

    def add_specific_constraints(self):
        """
        Add the speficic constraints stored in the database.
        """
        for constraint_type in TTConstraint.__subclasses__():
            for constr in constraint_type.objects.filter(Q(week=self.semaine) & Q(year=self.an) | Q(week__isnull=True)):
                constr.enrich_model(self)

    def update_objective(self):
        for i in self.wdb.instructors:
            self.obj += self.cost_I[i]
        for g in self.wdb.basic_groups:
            self.obj += self.cost_G[g]
        self.set_objective(self.obj)

    def add_TT_constraints(self):
        self.add_stabilization_constraints()

        self.add_core_constraints()

        self.add_rooms_constraints()

        self.add_slot_preferences()

        self.add_precedence_constraints()

        self.add_specific_constraints()

    def optimize(self, time_limit, solver, presolve=2):
        if solver=='gurobi':
            # ignore SIGINT while solver is running => SIGINT is still delivered to the solver, which is what we want
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.model.solve(GUROBI_CMD(keepFiles=1, msg=True, options=[("TimeLimit", time_limit),
                                                                        ("Presolve", presolve), ("MIPGapAbs", 0.2)]))
        else:
            self.model.solve(PULP_CBC_CMD(keepFiles=1, msg=True, presolve=presolve, maxSeconds=time_limit))
        status = LpStatus[self.model.status]
        print status
        if status == "Not Solved":
            print 'lpfile has been saved in FlOpTT-pulp.lp'
            return None
        elif status == "Optimal":
            return self.get_obj_coeffs()
        else:
            raise Exception("Strange result: nor Solved nor not Solved...")


    def solve(self, time_limit=3600, target_work_copy=None, solver='gurobi'):
        """
        Generates a schedule from the TTModel
        The solver stops either when the best schedule is obtained or timeLimit is reached.

        If stabilize_work_copy is None: does not move the scheduled courses whose year group is not in promo
        and fetches from the remote database these scheduled courses with work copy 0.

        If target_work_copy is given, stores the resulting schedule under this work copy number.
        If target_work_copy is not given, stores under the lowest working copy number that is greater than the maximum
        work copy numbers for the considered week.
        Returns the number of the work copy
        """
        print "\nLet's solve week #%g" % self.semaine

        if target_work_copy is None:
            local_max_wc = db.CoursPlace \
                .objects \
                .filter(cours__semaine=self.semaine,
                        cours__an=self.an) \
                .aggregate(Max('copie_travail'))['copie_travail__max']
            if local_max_wc is None:
                local_max_wc = -1

            target_work_copy = local_max_wc + 1

        print "Will be stored with work_copy = #%g" % target_work_copy

        print "Optimization started at", datetime.datetime.today().strftime('%Hh%M')
        result = self.optimize(time_limit, solver)
        print "Optimization ended at", datetime.datetime.today().strftime('%Hh%M')

        if result is not None:
            self.add_tt_to_db(target_work_copy)
            reassign_rooms(self.semaine, self.an, target_work_copy)
            return target_work_copy

    def run_solver(self, time_limit=3600, target_work_copy=None, save_log=False):
        if save_log:
            nom_log = 'logs/log' \
                      + datetime.datetime.today() \
                          .strftime('_%Y-%m-%d-%Hh%M_WEEK')
            nom_log += str(self.semaine) + '-' + str(self.an)

            print "log in ", nom_log
            with open(nom_log, 'w') as f:
                desc = os.dup(1)
                os.dup2(f.fileno(), 1)
                self.solve(self, time_limit=time_limit, target_work_copy=target_work_copy)
            os.dup2(desc, 1)
        else:
            self.solve(self, time_limit=time_limit, target_work_copy=target_work_copy)