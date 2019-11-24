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

from base.models import CourseType, Time, Day
from TTapp.models import slots_filter, days_filter
from TTapp.TTModel import max_weight
import random

possible_tutors = {
    'Caisse' : {'Annie', 'Elsa', 'Emilie', 'Jeremy', 'Marine', 'Nicolas', 'Manon'},
    'Ménage' : {'Florian', 'Leandre', 'Pierre'},
    'Proj' : {'Adelaide', 'Annie', 'Elsa', 'Frederic', 'Jeremy', 'Nicolas', 'Manon'},
    'Autre' : {'Annie', 'Elsa', 'Emilie', 'Jeremy', 'Marine', 'Nicolas', 'Florian',
               'Leandre', 'Pierre', 'Adelaide', 'Frederic', 'Manon'}
    }

salaries = {'Manon': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35},
            'Adelaide': {0: 28, 1: 28, 2: 28, 3: 28, 4: 28},
            'Frederic': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35},
            'Marine': {0: 26.5, 1: 26.5, 2: 26.5, 3: 26.5, 4: 26.5},
            'Emilie': {0: 17.5, 1: 17.5, 2: 17.5, 3: 17.5, 4: 17.5},
            'Nicolas': {0: 17.5, 1: 17.5, 2: 17.5, 3: 17.5, 4: 17.5},
            'Elsa': {0: 28, 1: 28, 2: 28, 3: 28, 4: 28},
            'Florian': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35},
            'Leandre': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35},
            'Pierre': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35},
            'Annie': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35},
            'Jeremy': {0: 35, 1: 35, 2: 35, 3: 35, 4: 35}}
temps_plein = {'Frederic',  'Manon'}
menage = {'Florian', 'Leandre', 'Pierre'}
temps_partiel = {'Marine', 'Elsa', 'Adelaide', 'Emilie', 'Nicolas',}
patrons = {'Annie', 'Jeremy'}
prorata = {}
for s in salaries:
    prorata[s] = salaries[s][0] / 35

def add_cosmo_specific_constraints(ttmodel):
    print("Et maintenant les contraintes du Cosmo!")
    projection = ttmodel.wdb.modules.get(abbrev="Proj")
    autre = ttmodel.wdb.modules.get(abbrev="Autre")
    controle = ttmodel.wdb.modules.get(abbrev="Ct_Men")
    local_var = ttmodel.add_var("UN")
    ttmodel.add_constraint(local_var, '==', 1)
    heures_max = {week: {} for week in ttmodel.wdb.weeks}
    heures_max['jour'] = {}
    heures_min = {week: {} for week in ttmodel.wdb.weeks}
    heures_min['jour'] = {}
    for rang, week in enumerate(ttmodel.wdb.weeks):
        for i in ttmodel.wdb.instructors:
            if i.username not in salaries:
                continue
            username = i.username
            if username in menage:
                heures_min[week][username] = 0
                heures_max[week][username] = 40
                heures_max['jour'][username] = 9
                heures_min['jour'][username] = 3
            elif username in patrons:
                heures_min[week][username] = 0
                heures_max[week][username] = 40
                heures_max['jour'][username] = 10
                heures_min['jour'][username] = 0
            else:
                heures_hebdo = salaries[username][rang]
                heures_min[week][username] = heures_hebdo - 5 * prorata[username] if heures_hebdo != 0 else 0
                heures_max[week][username] = heures_hebdo + 4 * prorata[username] if heures_hebdo != 0 else 0
                heures_max['jour'][username] = 9
                heures_min['jour'][username] = 4

    reus_d_equipe = [(45, Day.TUESDAY)]

    for i in ttmodel.wdb.instructors:
        if i.username not in salaries:
            continue
        ttmodel.nb_heures[i] = {}
        # Respecte les limites par semaine
        for week in ttmodel.wdb.weeks:
            ttmodel.nb_heures[i][week] = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                         for sl in slots_filter(ttmodel.wdb.slots, week=week)
                                         for c in set(ttmodel.wdb.possible_courses[i]) & ttmodel.wdb.compatible_courses[sl])

            ttmodel.add_constraint(ttmodel.nb_heures[i][week],
                                '<=',
                                heures_max[week][i.username],
                                '%s travaille pas trop s%s' % (i, week))

            ttmodel.add_constraint(ttmodel.nb_heures[i][week],
                                '>=',
                                heures_min[week][i.username],
                                '%s travaille assez s%s' % (i, week))

        ttmodel.nb_heures[i]['total'] = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                                    for sl in ttmodel.wdb.slots
                                                    for c in set(ttmodel.wdb.possible_courses[i]) &
                                                    ttmodel.wdb.compatible_courses[sl])

        if i.username not in patrons|menage:
            heures_periode = sum(salaries[i.username].values())
            ttmodel.add_constraint(ttmodel.nb_heures[i]['total'],
                                   '<=',
                                   heures_periode + 10 * prorata[i.username],
                                   "Globalement, %s travaille pas trop" % i.username)
            ttmodel.add_constraint(ttmodel.nb_heures[i]['total'],
                                   '>=',
                                   heures_periode - 10 * prorata[i.username],
                                   "Globalement, %s travaille assez" % i.username)
        # Respecte les limites par jour
        for day in ttmodel.wdb.days:
            ttmodel.nb_heures[i][day] = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)]*sl.duration/60
                                         for sl in slots_filter(ttmodel.wdb.slots, day=day)
                                         for c in set(ttmodel.wdb.possible_courses[i]) & ttmodel.wdb.compatible_courses[sl])

            ttmodel.add_constraint(ttmodel.nb_heures[i][day],
                                   '<=',
                                   heures_max['jour'][i.username],
                                   '%s travaille pas trop %s' % (i, day))
            #if not ttmodel.forced_IBD[i, day]:
            if (day.week, day.day) not in reus_d_equipe:
                ttmodel.add_constraint(heures_min['jour'][i.username] * ttmodel.IBD[(i, day)] -
                                       ttmodel.nb_heures[i][day],
                                       '<=',
                                       0,
                                       '%s travaille assez %s' % (i, day))
            # else:
            #     print("réu d'équipe pour %s le %s" % (i, day))

    ttmodel.Module_per_day = {}
    for i in ttmodel.wdb.instructors:
        for m in ttmodel.wdb.possible_modules[i]:
            ttmodel.Module_per_day[(i, m)] = {}
            for d in ttmodel.wdb.days:
                ttmodel.Module_per_day[(i, m)][d] = ttmodel.add_var("Mod_per_day(%s,%s,%s)" % (i, m, d))
                # Linking the variable to the TT
                dayslots = ttmodel.wdb.slots_by_day[d]
                card = 2 * len(dayslots)
                expr = ttmodel.lin_expr()
                expr += card * ttmodel.Module_per_day[(i, m)][d]
                for c in set(ttmodel.wdb.courses.filter(module=m)) & ttmodel.wdb.possible_courses[i]:
                    for sl in dayslots & ttmodel.wdb.compatible_slots[c]:
                        expr -= ttmodel.TTinstructors[(sl, c, i)]
                ttmodel.add_constraint(expr, '>=', 0, "Mod_per_day(%s,%s,%s)" % (i, m, d))

    # One module max per day : Enlevé pour passer de la caisse au contrôle
    for d in ttmodel.wdb.days:
        for i in ttmodel.wdb.instructors:
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.Module_per_day[(i, m)][d] for m in ttmodel.wdb.possible_modules[i]),
                '<=',
                2,
                'Two modules max per day %s-%s' % (i, d))

    heures_par_jour = {}
    amplitude = {}
    for mod in ttmodel.wdb.modules:
        for d in ttmodel.wdb.days:
            SC = ttmodel.wdb.sched_courses.filter(cours__semaine=d.week, day=d.day, cours__module=mod)\
                                          .exclude(cours__tutor__username__in=menage)
            heures_par_jour[(mod, d)] = sum(sc.cours.type.duration for sc in SC)/60
            if SC.exists():
                amplitude[(mod, d)] = (max(sc.start_time + sc.cours.type.duration for sc in SC)
                                       - min(sc.start_time for sc in SC))/60
            else:
                amplitude[(mod, d)] = 0

    # One or two tutors max per day
    ttmodel.add_warning(None, "<9h: Un seul salarié. >9h: Pas plus de 2 salariés par jour sur un même poste")
    for m in ttmodel.wdb.modules:
        if m.abbrev == 'Autre':
            continue
        g = ttmodel.wdb.groups.get(nom=m.abbrev)
        for d in ttmodel.wdb.days:
            if amplitude[(m, d)] <= 9:
                # limit = 1
                limit = 2
            else:
                limit = 2
            if m.abbrev == 'Ct_Men':
                limit += 1
            cost = ttmodel.sum(ttmodel.Module_per_day[(i, m)][d] for i in
                               ttmodel.wdb.possible_tutors[m] if i.username not in patrons) \
                - limit * local_var
            ttmodel.add_to_group_cost(g, cost)
            ttmodel.add_constraint(cost, '<=', 0, '%g max tutor per day %s-%s' % (limit, m, d))

    # Pas de journée de plus de 9h --> Inutile si "pas de trous"
    for i in ttmodel.wdb.instructors:
        if i.username in menage:
            continue
        for d in ttmodel.wdb.days:
            for sl in ttmodel.wdb.slots_by_day[d]:
                for sl2 in ttmodel.wdb.slots_by_day[d]:
                    if sl2.end_time - sl.start_time > 9 * 60:
                        ttmodel.add_constraint(
                            ttmodel.sum(ttmodel.TTinstructors[sl, c, i]
                                     for c in ttmodel.wdb.possible_courses[i] & ttmodel.wdb.compatible_courses[sl])
                            +
                            ttmodel.sum(ttmodel.TTinstructors[sl2, c, i]
                                     for c in ttmodel.wdb.possible_courses[i] & ttmodel.wdb.compatible_courses[sl2]),
                            '<=',
                            1,
                            '%s-%s- Pas en meme temps %s-%s' % (i, d, sl, sl2))

    # # Assure les heures par poste déclarés --> INUTILE AVEC LE NOUVEAU wdb.compatible_slots / courses...
    # for week in ttmodel.wdb.weeks:
    #     for ct in CourseType.objects.all():
    #         for mod in ttmodel.wdb.modules:
    #             courses = set(ttmodel.wdb.courses.filter(module=mod, type=ct, semaine=week))
    #             if len(courses) == 0:
    #                 continue
    #             if ct.duration == 60:
    #                 nb_slots = sum(int(nb_salaries['A'][d.day][heure][mod.abbrev])
    #                                for heure in range(8, 25)
    #                                for d in days_filter(ttmodel.wdb.days, week=week))
    #             else:
    #                 nb_slots = 0
    #                 for heure in range(8, 25):
    #                     for d in ttmodel.wdb.days:
    #                         if nb_salaries['A'][d.day][heure][mod.abbrev] == 0.5:
    #                             nb_slots += 1
    #             print(ct, mod, nb_slots, len(courses))
    #             if len(courses) != nb_slots:
    #                 print('Problème pour mod %s and ct %s' % (mod, ct))
    #             else:
    #                 for sl in slots_filter(ttmodel.wdb.slots, course_type=ct, week=week):
    #                     if nb_salaries['A'][sl.day.day][sl.start_time // 60][mod.abbrev] == sl.duration / 60:
    #                         c = courses.pop()
    #                         ttmodel.add_constraint(ttmodel.TT[(sl, c)],
    #                                             '==',
    #                                             1, "%s_in_%s"%(c, sl))
    dernier_creneau = {}
    nb_trous = {}
    for i in ttmodel.wdb.instructors:
        for d in ttmodel.wdb.days:
            for sl in ttmodel.wdb.slots_by_day[d]:
                dernier_creneau[i, sl] = ttmodel.add_var("%s est un creneau de fin pour %s" % (sl, i.username))
                # Si c'est le dernier créneau, il est busy
                ttmodel.add_constraint(
                    dernier_creneau[i, sl] - ttmodel.IBS[i, sl], '<=', 0, "last->busy_%s_%s" % (sl, i.username)
                    )
                # si c'est le dernier créneau, y'en a pas juste après
                ttmodel.add_constraint(
                    ttmodel.sum(ttmodel.IBS[i, sl_suivant]
                                for sl_suivant in ttmodel.wdb.slots if sl_suivant.is_successor_of(sl))
                    + 10 * dernier_creneau[i, sl]
                    , '<=', 10, "last_%s_%s_A" % (sl, i.username)
                    )
                # si c'est pas le dernier créneau, y'en a après OU il est pas busy
                ttmodel.add_constraint(
                    ttmodel.sum(ttmodel.IBS[i, sl_suivant]
                                for sl_suivant in ttmodel.wdb.slots if sl_suivant.is_successor_of(sl))
                    + (local_var - ttmodel.IBS[i, sl])
                    + dernier_creneau[i, sl]
                    , '>=', 1, "last_%s_%s_B" % (sl, i.username)
                    )

            nb_trous[i, d] = ttmodel.sum(dernier_creneau[i, sl] for sl in ttmodel.wdb.slots_by_day[d]) \
                             - ttmodel.IBD[(i, d)]

    for d in ttmodel.wdb.days:
        # diff_proj = amplitude[projection, d] - heures_par_jour[projection, d]
        # diff_autre = amplitude[autre, d] - heures_par_jour[autre, d]
        # diff_controle = amplitude[controle, d] - heures_par_jour[controle, d]
        # trouEs_autre = set()
        # trouEs_controle = set()
        # trouEs_proj = set()
        # if diff_proj >= 1:
        #     pas_de_chance = ttmodel.wdb.instructors.get(username=random.choice(list(possible_tutors['Proj']-patrons)))
        #     trouEs_proj.add(pas_de_chance)
        #     print("%s: trou imposé en proj à %s (pas de chance)..." % (d, pas_de_chance.username))
        # if diff_autre >= 1:
        #     for c in ttmodel.wdb.sched_courses.filter(day=d.day, cours__semaine=d.week, cours__module=autre)\
        #             .exclude(cours__tutor=None).exclude(cours__tutor__username__in=menage):
        #         trouEs_autre.add(c.tutor)
        #     if len(trouEs_autre) > 1:
        #         trouEs_autre = set()
        #     if trouEs_autre:
        #         print(d, ": trou imposé en Autre...", trouEs_autre)
        # if diff_controle >= 1:
        #     for c in ttmodel.wdb.sched_courses.filter(day=d.day, cours__semaine=d.week, cours__module=controle)\
        #             .exclude(cours__tutor=None).exclude(cours__tutor__username__in=menage):
        #         trouEs_controle.add(c.tutor)
        #     if len(trouEs_controle) > 1:
        #         trouEs_controle = set()
        #     if trouEs_controle:
        #         print(d, ": trou imposé en Controle...", trouEs_controle)
        for i in ttmodel.wdb.instructors:
        #     if i.username in menage | patrons:
        #         continue
        #     if i in trouEs_controle | trouEs_autre | trouEs_proj:
        #         trous_max = 1
        #     else:
        #         trous_max = 0
            # ttmodel.add_constraint(nb_trous[i, d], '<=', trous_max, "%g trous max %s %s" % (trous_max, i.username, d))
            if (d.week, d.day) not in reus_d_equipe:
                ttmodel.add_to_inst_cost(i, nb_trous[i, d]*1000)
            else:
                ttmodel.add_to_inst_cost(i, (nb_trous[i, d] + ttmodel.IBD[i, d]) * 1000)
    # Pas de trou pour un prof donné!
    # for d in ttmodel.wdb.days:
    #     diff_proj = amplitude[projection, d] - heures_par_jour[projection, d]
    #     diff_autre = amplitude[autre, d] - heures_par_jour[autre, d]
    #     diff_controle = amplitude[controle, d] - heures_par_jour[controle, d]
    #     trouEs = set()
    #     if diff_proj > 0:
    #         print(d, ": trou imposé en proj!")
    #     if diff_autre > 0:
    #         print(d, ": trou imposé en Autre...", end=' ')
    #         for c in ttmodel.wdb.sched_courses.filter(day=d.day, cours__semaine=d.week, cours__module=autre):
    #             trouEs.add(c.tutor)
    #         print(trouEs)
    #     if diff_controle > 0:
    #         print(d, ": trou imposé en Controle...", end=' ')
    #         for c in ttmodel.wdb.sched_courses.filter(day=d.day, cours__semaine=d.week, cours__module=controle):
    #             trouEs.add(c.tutor)
    #         print(trouEs)
    #     for i in ttmodel.wdb.instructors:
    #         if i.username in menage:
    #             continue
    #         if i in trouEs:
    #             trou_max = max(diff_controle, diff_autre)
    #         elif i in projection.possible_tutors.all():
    #             trou_max = diff_proj
    #         else:
    #             trou_max = 0.5
    #         heure = ttmodel.wdb.course_types.get(name='OS')
    #         slots = slots_filter(ttmodel.wdb.slots_by_day[d], course_type=heure)
    #         for sl1 in slots:
    #             for sl2 in slots:
    #                 if sl2 > sl1:
    #                     both = ttmodel.add_conjunct(ttmodel.IBS[i, sl1], ttmodel.IBS[i, sl2])
    #                     ttmodel.add_constraint(
    #                         ((sl2.start_time - sl1.end_time) * both
    #                          - ttmodel.sum(ttmodel.IBS[i, sl] * sl.duration
    #                                        for sl in ttmodel.wdb.slots_by_day[d] if sl1 < sl < sl2)
    #                          )/60,
    #                         '<=',
    #                         trou_max, "%s_%s_cours_entre_%s_et_%s"%(i, d, sl1.end_time, sl2.start_time))

    # # Pierre fait le ménage Lundi + mardi + mercredi + jeudi
    # # Léandre et Florian tournent sur le week-end : l'un fait vendredi + samedi matin ménage,
    # # l'autre fait dimanche ménage + contrôle, et on inverse une semaine sur deux...
    # # CA FONCTIONNE!!!
    # Inutile vu l'affectation - Plutôt :
    ttmodel.add_constraint(
        ttmodel.sum(ttmodel.TTinstructors[sl, c, i]
                    for i in ttmodel.wdb.instructors if i.username in menage
                    for c in ttmodel.wdb.possible_courses[i] if c.tutor is None
                    for sl in ttmodel.wdb.compatible_slots[c]),
        '==',
        0,
        'Menage ==> Menage'
    )
    # ttmodel.add_warning(None, "Répartition du ménage entre Pierre, Léandre et Florian")
    #
    # Pierre = ttmodel.wdb.instructors.get(username='Pierre')
    # lundi_jeudi = days_filter(ttmodel.wdb.days, index_in=range(4))
    # ttmodel.add_constraint(
    #     ttmodel.sum(ttmodel.TT[(sl,c)] - ttmodel.TTinstructors[(sl, c, Pierre)]
    #                 for d in lundi_jeudi
    #                 for sl in ttmodel.wdb.slots_by_day[d]
    #                 for c in ttmodel.wdb.possible_courses[Pierre] & ttmodel.wdb.compatible_courses[sl]),
    #     '==',
    #     0, "Pierre fait le ménage Lundi-mardi-mercredi-jeudi")
    #
    # choix=[Leandre, Florian, Pierre]
    #
    # for week in ttmodel.wdb.weeks:
    #     vendredi_samedi = days_filter(ttmodel.wdb.days, index_in=range(4,6), week=week)
    #     prof1=choix[week % 2]
    #     prof2=choix[(week+1) % 2]
    #     ttmodel.add_constraint(
    #         ttmodel.sum(ttmodel.TT[(sl,c)] - ttmodel.TTinstructors[(sl, c, prof1)]
    #                     for d in vendredi_samedi
    #                     for sl in slots_filter(ttmodel.wdb.slots_by_day[d], apm=Time.AM)
    #                     for c in ttmodel.wdb.possible_courses[prof1] & ttmodel.wdb.compatible_courses[sl]),
    #         '==',
    #         0, "sem %s - %s fait vendredi + samedi matin ménage" % (week, prof1))
    #     ttmodel.add_constraint(
    #         ttmodel.sum(ttmodel.TTinstructors[(sl, c, prof)]
    #                     for prof in choix
    #                     for d in vendredi_samedi
    #                     for sl in slots_filter(ttmodel.wdb.slots_by_day[d], apm=Time.PM)
    #                     for c in ttmodel.wdb.possible_courses[prof1] & ttmodel.wdb.compatible_courses[sl]),
    #         '==',
    #         0, "sem %s - Le vendredi et samedi le Ct/Mén c'est du controle" % (week))
    #
    #     dimanche = days_filter(ttmodel.wdb.days, index=6, week=week)
    #     ttmodel.add_constraint(
    #         ttmodel.sum(ttmodel.TT[(sl,c)] - ttmodel.TTinstructors[(sl, c, prof2)]
    #                     for d in dimanche
    #                     for sl in slots_filter(ttmodel.wdb.slots_by_day[d], week=week)
    #                     for c in ttmodel.wdb.possible_courses[prof2] & ttmodel.wdb.compatible_courses[sl]),
    #         '==',
    #         0, "sem %s - %s fait ménage+contrôle le dimanche" % (week, prof2))

    # # Si on fait caisse et contrôle, le contrôle est après la caisse
    # vendredi_samedi = days_filter(ttmodel.wdb.days, index_in=range(4, 6))
    # Caisse = ttmodel.wdb.modules.get(abbrev="Caisse")
    # Controle = ttmodel.wdb.modules.get(abbrev="Ct/Mén")
    # for i in ttmodel.wdb.instructors.filter(username__in=possible_tutors['Caisse']):
    #     for d in vendredi_samedi:
    #         Caisse_et_controle = ttmodel.add_conjunct(ttmodel.Module_per_day[(i, Caisse)][d],
    #                                                   ttmodel.Module_per_day[(i, Controle)][d])
    #         for sl1 in slots_filter(ttmodel.wdb.slots, day=d):
    #             for sl2 in slots_filter(ttmodel.wdb.slots, day=d, is_after=sl1):
    #                 ttmodel.add_constraint(
    #                     Caisse_et_controle -
    #                     ttmodel.sum(ttmodel.TTinstructors[(sl1, c, i)]
    #                                 for c in set(ttmodel.wdb.possible_courses[i])
    #                                 & ttmodel.wdb.compatible_courses[sl1]
    #                                 & set(ttmodel.wdb.courses.filter(module__abbrev="Ct/Mén"))) -
    #                     ttmodel.sum(ttmodel.TTinstructors[(sl2, c, i)]
    #                                 for c in set(ttmodel.wdb.possible_courses[i])
    #                                 & ttmodel.wdb.compatible_courses[sl2]
    #                                 & set(ttmodel.wdb.courses.filter(module__abbrev="Caisse"))),
    #                     '>=',
    #                     0,
    #                     'Caisse avant Controle %s-%s-%s'%(i, sl1, sl2))

    # Coupure de 11h au moins!
    ttmodel.add_warning(None, "Une Coupure d'au moins 11h entre 2 jours consécutifs !")
    for day in ttmodel.wdb.days:
        if day.week == max(ttmodel.wdb.weeks) and day.day==Day.SUNDAY:
            continue
        successive_day = ttmodel.wdb.day_after[day]
        for i in ttmodel.wdb.instructors:
            deux_jours_d_affilee = ttmodel.add_conjunct(ttmodel.IBD[(i,day)], ttmodel.IBD[(i,successive_day)])
            for sl1 in slots_filter(ttmodel.wdb.slots, day=day, apm=Time.PM):
                for sl2 in slots_filter(ttmodel.wdb.slots, day=successive_day, apm=Time.AM):
                    if sl2.start_time+24*60 - sl1.end_time < 11*60:
                        ttmodel.add_constraint(
                            ttmodel.IBS[(i,sl1)] + ttmodel.IBS[(i,sl2)],
                            '<=',
                            1,
                            '11h de coupure %s-%s-%s' % (i, sl1, sl2))

    # sur 5 semaines, pendant lesquelles chaque personne a
    # un week-end de trois jours de repos (samedi dimanche lundi)
    #       + un jour de week-end la semaine suivante (samedi ou dimanche).
    # (qu'on essaie d'être le plus régulier possible).
    jours_de_WE = days_filter(ttmodel.wdb.days, index_in=[5,6])

    if len(ttmodel.wdb.weeks) == 5:
        ttmodel.add_warning(None, "Au moins 1 WE de 3 jours par salarié·e 1 jour de WE en plus (sauf ménage et Nicolas)")
        ttmodel.add_warning(None, "Pas plus de 2 WE par personne")
        ttmodel.add_warning(None, "Maximiser les WE et quasi-WE")
        for salarie in ttmodel.wdb.instructors:
            if salarie.username == 'Nicolas':
                parite = ttmodel.wdb.weeks[0] % 2
                # if parite == 0:
                #     days_nico = [days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[0], index=6).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[1], index=0).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[2], index=6).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[3], index=0).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[4], index=6).pop()]
                # else:
                #     days_nico = [days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[0], index=0).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[1], index=6).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[2], index=0).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[3], index=6).pop(),
                #                  days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[4], index=0).pop()]
                #
                # ttmodel.add_constraint(
                #     ttmodel.sum(ttmodel.IBD[salarie, jour] - ttmodel.forced_IBD[salarie, jour] * local_var for jour in days_nico),
                #     '==',
                #     0,
                #     "Deal de Nicolas")
            elif salarie.username not in menage:
                ttmodel.add_constraint(ttmodel.sum(ttmodel.WE_3jours[salarie, week] for week in ttmodel.wdb.weeks),
                                       '>=',
                                       1,
                                       "Au moins 1 WE de 3 jours pour %s" % salarie.username)
                ttmodel.add_constraint(
                    ttmodel.sum(ttmodel.IBD[salarie, jour] for jour in jours_de_WE),
                    '<=',
                    7,
                    "Au moins 3 jours de WE %s" % salarie.username)
                if salarie.username in temps_plein:
                    ttmodel.add_constraint(ttmodel.sum(ttmodel.WE[salarie, week] for week in ttmodel.wdb.weeks),
                                           '<=',
                                           2,
                                           "Pas plus de 2 WE pour %s" % salarie.username)
                if salarie.username not in patrons:
                    ttmodel.add_constraint(ttmodel.sum(ttmodel.quasiWE[salarie, week] for week in ttmodel.wdb.weeks),
                                           '<=',
                                           3,
                                           "Pas plus de 3 quasi-WE pour %s" % salarie.username)

            if salarie.username not in menage:
                ttmodel.add_to_inst_cost(salarie, -5 * ttmodel.sum(ttmodel.quasiWE[salarie, week]
                                                                   for week in ttmodel.wdb.weeks))
                ttmodel.add_to_inst_cost(salarie, -10 * ttmodel.sum(ttmodel.WE[salarie, week]
                                                                    + ttmodel.WE_3jours[salarie, week]
                                                                    for week in ttmodel.wdb.weeks))

            # Les patrons peuvent travailler le WE, mais le coût a été rendu très grand...
            # if salarie.username in patrons:
            #     ttmodel.add_constraint(ttmodel.sum(ttmodel.IBD[salarie, d] - ttmodel.forced_IBD[salarie, d] * local_var
            #                                        for d in jours_de_WE),
            #                            '==',
            #                            0,
            #                            "Pas de travail le WE - %s" % salarie.username)


    ttmodel.add_warning(None, "Pas plus de 6 jours de travail consécutifs")
    for day in (days_filter(ttmodel.wdb.days, week_in=ttmodel.wdb.weeks[:-1])
                | days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[-1], index=0)):
        for salarie in ttmodel.wdb.instructors:
            expr = ttmodel.IBD[salarie, day]
            suivant = day
            for _ in range(6):
                suivant = ttmodel.wdb.day_after[suivant]
                expr += ttmodel.IBD[salarie, suivant]
            ttmodel.add_constraint(expr, '<=', 6, "Pas plus de 6 jours consécutifs %s-%s" % (salarie, day))

    # Les temps partiels peuvent avoir trois jours de repos par semaine avec au moins deux jours consécutifs.
    # Le reste des semaines, les personnes à temps plein ont deux jours de repos par semaine
    ttmodel.add_warning(None, "Pas plus de 4/5 jours par semaine")
    for week in ttmodel.wdb.weeks:
        for salarie in ttmodel.wdb.instructors:
            if salarie.username in temps_partiel:
                limit = 4
            else:
                limit = 5
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.IBD[salarie, day] for day in days_filter(ttmodel.wdb.days, week=week)), '<=', limit,
                "%s - Pas plus de %d jours semaine %s"%(salarie, limit, week))

    ttmodel.add_warning(None, "Au moins 2 jours de repos consecutifs par semaine (sauf apres un WE de 3 jours")
    for week in ttmodel.wdb.weeks:
        for salarie in ttmodel.wdb.instructors:
            days = days_filter(ttmodel.wdb.days, week=week)
            expr = ttmodel.lin_expr()
            for index in range(len(days)-1):
                jours = list(days_filter(days, index_in=[index, index+1]))
                les_deux=ttmodel.add_var("Ni %s Ni %s_%s" % (jours[0], jours[1], salarie.username))
                ttmodel.add_constraint(les_deux + ttmodel.IBD[salarie, jours[0]] + ttmodel.IBD[salarie, jours[1]],
                                       '>=', 1)
                ttmodel.add_constraint(2*les_deux + ttmodel.IBD[salarie, jours[0]] + ttmodel.IBD[salarie, jours[1]],
                                       '<=', 2)
                expr += les_deux
            if ttmodel.wdb.weeks.index(week) == 0:
                ttmodel.add_constraint(expr, '>=', 1, "2_jours_consecutifs_%s_s%s" % (salarie.username, week))
            else:
                ttmodel.add_constraint(expr + ttmodel.WE_3jours[salarie, week-1], '>=', 1,
                                       "2_jours_consecutifs_ou_WE_de_3_jours_%s_s%s" % (salarie.username, week))

    # NB : les slots compatibles sont ceux de semaine (hors WE), de 9h à 18h
    ttmodel.add_warning(None, "Les cours à suspens sont placés par blocs de 3h au moins")
    for week in ttmodel.wdb.weeks:
        for i in ttmodel.wdb.instructors:
            cours_a_suspens = ttmodel.wdb.courses.filter(tutor=i, suspens=True, semaine=week)
            if not cours_a_suspens.exists():
                continue
            for day in days_filter(ttmodel.wdb.days, week=week):
                nb_h_a_suspens_du_jour = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                                     for sl in slots_filter(ttmodel.wdb.slots, day=day)
                                                     for c in set(cours_a_suspens) & ttmodel.wdb.compatible_courses[sl])
                # si i a des heures variables à faire, suspens est_i à 1
                # s'il est à 1, les heures à faire sont au moins à 3!
                suspens_i = ttmodel.add_var("%s fait des heures variables %s" % (i, day))
                card = 20
                expr = card * suspens_i - nb_h_a_suspens_du_jour
                ttmodel.add_constraint(expr, '>=', 0)
                ttmodel.add_constraint(expr, '<=', card - 3)
                # Pas plus de 7 par jour
                ttmodel.add_constraint(nb_h_a_suspens_du_jour, '<=', 7)


    ttmodel.add_warning(None, "Si on fait la fermeture le soir sur un poste, alors c'est pour 4h30 au moins")
    for day in ttmodel.wdb.days:
        for poste in ttmodel.wdb.modules.filter(abbrev__in=['Caisse', 'Proj']):
            if not ttmodel.wdb.sched_courses.filter(day=day.day,
                                                    cours__semaine=day.week,
                                                    cours__module=poste).exists():
                print('Pas de cours de %s %s' %(poste, day) )
                continue
            last_start_time = max(sl.start_time for sl in ttmodel.wdb.sched_courses.filter(day=day.day,
                                                                                           cours__semaine=day.week,
                                                                                           cours__module=poste))
            last_sched_course = ttmodel.wdb.sched_courses.get(day=day.day, cours__semaine=day.week, cours__module=poste,
                                                              start_time=last_start_time)
            last_course = last_sched_course.cours
            slots = ttmodel.wdb.compatible_slots[last_course]
            if len(slots) > 1:
                print("Plusieurs slots pour %s" % last_sched_course)
                continue
            last_slot = list(slots)[0]
            for i in ttmodel.wdb.possible_tutors[poste] & ttmodel.wdb.possible_tutors[last_course]:
                # last_i = ttmodel.add_var("%s %s ferme en %s" % (day, i, poste.abbrev))
                # ttmodel.add_constraint(last_i - ttmodel.IBS[(i, last_slot)], '==', 0,
                #                        "Fermeture %s par %s en %s" % (day, i, poste.abbrev))
                heures_de_soiree = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                               for sl in slots_filter(ttmodel.wdb.slots, day=day)
                                               if sl.start_time >= last_start_time - 4*60
                                               for c in ttmodel.wdb.compatible_courses[sl]
                                               & ttmodel.wdb.possible_courses[i] if c.module == poste
                                               )
                                               # & ttmodel.wdb.courses.filter(module=poste))
                card = 20
                expr = card * ttmodel.TTinstructors[(last_slot, last_course, i)] - heures_de_soiree
                ttmodel.add_constraint(expr, '<=', card - 4.5, "%s %s ferme en %s" % (day, i, poste.abbrev))

    ttmodel.add_warning(None, "Fred et Adelaïde sont principalement en proj")
    projectionnistes = {"Frederic", "Adelaide"}
    cout_si_les_projectionnistes_font_autre_chose = 0.5
    for projectionniste in ttmodel.wdb.instructors:
        if projectionniste.username not in projectionnistes:
            continue
        heures_hors_projection = ttmodel.sum(ttmodel.TTinstructors[(sl, c, projectionniste)] * c.type.duration / 60
                                             for c in set(ttmodel.wdb.courses.exclude(module=projection))
                                             & ttmodel.wdb.possible_courses[projectionniste]
                                             for sl in ttmodel.wdb.compatible_slots[c])
        ttmodel.add_to_inst_cost(projectionniste,
                                 cout_si_les_projectionnistes_font_autre_chose * heures_hors_projection)

    # Semaine 4, peu d'heures patrons, et au pire en proj!
    if ttmodel.wdb.weeks == 5:
        semaine_4 = ttmodel.wdb.weeks[3]
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TTinstructors[sl, c, i]
                                           for sl in slots_filter(ttmodel.wdb.slots, week=semaine_4)
                                           for i in ttmodel.wdb.instructors if i.username in patrons
                                           for c in ttmodel.wdb.compatible_courses[sl] & ttmodel.wdb.possible_courses[i]
                                           if c.module != projection),
                               '==', 0, "Patrons en proj en semaine 4 ")

    # Compteur des heures réellement effectuées par semaine et par jour
    heures_reelles_hebdo = {semaine: {} for semaine in ttmodel.wdb.weeks}
    heures_reelles_quotidiennes = {jour: {} for jour in ttmodel.wdb.days}
    for salarie in ttmodel.wdb.instructors:
        if salarie.username not in salaries:
            continue
        for semaine in ttmodel.wdb.weeks:
            heures = ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie] * c.type.duration / 60
                                 for c in ttmodel.wdb.possible_courses[salarie]
                                 for sl in slots_filter(ttmodel.wdb.compatible_slots[c], week=semaine))
            heures_reelles_hebdo[semaine][salarie] = heures
        for jour in ttmodel.wdb.days:
            heures = ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie] * c.type.duration / 60
                                 for c in ttmodel.wdb.possible_courses[salarie]
                                 for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=jour))
            heures_reelles_quotidiennes[jour][salarie] = heures


    diff_max_entre_patrons_par_semaine = 5
    ttmodel.add_warning(None, "Max %d heures par semaine de différence entre les patrons"
                        % diff_max_entre_patrons_par_semaine)
    Annie = Jeremy = None
    for i in ttmodel.wdb.instructors:
        if i.username == 'Annie':
            Annie = i
        elif i.username == 'Jeremy':
            Jeremy = i
    for semaine in ttmodel.wdb.weeks:
        ttmodel.add_constraint(heures_reelles_hebdo[semaine][Annie] - heures_reelles_hebdo[semaine][Jeremy],
                               '<=', diff_max_entre_patrons_par_semaine,
                               "diff max de %g entre A et J semaine %g" % (diff_max_entre_patrons_par_semaine, semaine))
        ttmodel.add_constraint(heures_reelles_hebdo[semaine][Jeremy] - heures_reelles_hebdo[semaine][Annie],
                               '<=', diff_max_entre_patrons_par_semaine,
                               "diff max de %g entre J et A semaine %g" % (diff_max_entre_patrons_par_semaine, semaine))
    

    ttmodel.add_warning(None, "Eviter que les deux boss bossent le même jour")
    cout_si_les_deux_patrons_travaillent = 5
    les_deux_patrons_travaillent = {}
    contrainte = False
    for d in ttmodel.wdb.days:
        les_deux_patrons_travaillent[d] = ttmodel.add_conjunct(ttmodel.IBD[Annie,d], ttmodel.IBD[Jeremy, d])
        if ttmodel.forced_IBD[Annie, d] + ttmodel.forced_IBD[Jeremy, d] < 2:
            if contrainte:
                ttmodel.add_constraint(les_deux_patrons_travaillent,
                                       '==', 0,
                                       "Un patron max bosse %s" % d)
            else:
                ttmodel.obj += les_deux_patrons_travaillent[d] * cout_si_les_deux_patrons_travaillent

    ttmodel.add_warning(None, "Minimiser le nombre de jours de travail pour chaque salarié⋅e")
    # (Si ça ne dépasse pas la borne posée dans pref_slots_per_day)
    for salarie in ttmodel.wdb.instructors:
        if salarie.username not in salaries:
            continue
        for rang, semaine in enumerate(ttmodel.wdb.weeks):
            cout_jours_de_trop = 0
            # need to be sorted
            frontier_pref_busy_days = [salarie.pref_hours_per_day * d for d in range(6, 0, -1)]
            nb_heures_a_faire = salaries[salarie.username][rang]
            nb_days = 7

            for fr in frontier_pref_busy_days:
                if nb_heures_a_faire <= fr:
                    cout_jours_de_trop += ttmodel.IBD_GTE[semaine][nb_days][salarie]
                    nb_days -= 1
                else:
                    break
            ttmodel.add_to_inst_cost(salarie, ttmodel.min_bd_i * cout_jours_de_trop)

        for d in ttmodel.wdb.days:
            ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c, salarie] * c.type.duration / 60
                                               for c in ttmodel.wdb.possible_courses[salarie]
                                               for sl in slots_filter(ttmodel.wdb.slots, week=d.week,
                                                                      day=d.day)
                                               & ttmodel.wdb.compatible_slots[c]),
                                   '<=',
                                   salarie.pref_hours_per_day + 2,
                                   name='max_heures_par_jour_%s_%s' % (salarie, d))

    for reu in reus_d_equipe:
        if reu[0] in ttmodel.wdb.weeks:
            jour = days_filter(ttmodel.wdb.days, week=reu[0],day=reu[1]).pop()
            for salarie in ttmodel.wdb.instructors:
                if salarie.username in salaries:
                    ttmodel.add_constraint(ttmodel.IBD[salarie, jour], '==', 1, "reu d'equipe %s" % salarie.username)

    # A RAJOUTER
    # - Un changement de poste max par jour (Post PROD)
    # - Fred, Adélaïde en priorité (et pas les patrons)
    #   Au moins Fred, Adélaïde un mercredi matin par fanzine.

    # ELSA :
    # - le WE de 3 jours idéal: du vendredi 17h au lundi 17h
    # - que mes 3 jours de repos se suivent
    # - faire des grosses journées (9h30) pour éventuellement ne travailler que 3 jours/semaine
    #   (car je fais un tps partiel à 28h/semaine)
    # - un quasi WE c'est du vendredi 17h au dimanche 17h ou du samedi 17h au lundi 17h
    # - dans l'idéal je voudrais avoir deux WE
    # - je veux bien avoir plus de soirées que de journées pour que mon planning me plaise davantage
    # - je veux bosser en soirée trois jours avant l'arrivée du fanzine et deux jours après
    #   (le fanzine est livré un mercredi : travailler en soirée le dimanche, lundi et mardi qui précèdent
    #   ainsi que les mercredi et jeudi qui suivent.)

    # NICOLAS
    # - avoir le max de demi-journées consécutives de repos (par ex : mardi aprém + mercredi + jeudi + vendredi matin)
    # - avoir le maximum de jours de repos (donc faire les services les plus longs possibles)
    # - par ailleurs j'ai des contraintes familiales que j'ai négociées avec Annie et Jeremy,
    # à savoir une alternance toutes les deux semaines d'un dimanche-lundi, sauf cas particulier
    # (par exemple je bosse le 30 alors que je ne devrais pas).
    # Le plus simple, je pense, serait de m'autoriser à mettre les sens interdit sur ces jours-là
    # (ce qui suppose donc 16 sens interdits, et la possibilité d'en mettre les dimanches, ce que j'ai fait ce mois-ci).
    #  Et tu peux m'enlever l'obligation d'avoir un samedi dimanche par fanzine.

    # EMILIE :
    # Le weekend de 3 jours vraiment idéal serait d'être en weekend le vendredi en fin d'après-midi (au plus tard 20h)
    # et de reprendre le mardi en début d'après-midi (au plus tôt 13h).
    # WE = Etre de repos le samedi et le dimanche.
    # Quasi-WE : Etre de repos le vendredi et le samedi, ou avoir son samedi soir, le dimanche et le lundi.
    # Concernant d'autres remarques, personnellement je serais ravie sur un planning de 5 semaines de pouvoir
    # - avoir un weekend de 3 jours,
    # + un autre vrai weekend (repos samedi et dimanche),
    # + idéalement au moins une soirée de libre par semaine en dehors des jours de repos.
    # + weekends de 4 jours occasionnelement .

    # MARINE:
    # un WE de 3 jours idéal : du vendredi inclus et jusqu'au dimanche inclus.
    # un WE : du vendredi 18h au dimanche inclus.
    # un quasi-WE : avoir son samedi/dimanche ou encore son vendredi/samedi ou son dimanche/lundi.
    #
    # jours de congés d'affilés ( mardi/mercredi/jeudi) et fixes si possibles
    #
    # Equilibre entre semaines de journées et semaines de soirées.
    # Ce que j’appelle « journée", c’est ne pas faire de clôture (jusqu’à minuit).
    # 2 WE si possible (sauf si ça implique de se faire tous les autres wkd en clôture)
    # Hors été, favorable à une amplitude plus grosse pour pouvoir avoir plus de week-end
    # Si je fais de la distribution ("Autre") je ne fais rien d'autre dans la journée.

    # Convention collective (Exploitation cinématographique)
    #
    #