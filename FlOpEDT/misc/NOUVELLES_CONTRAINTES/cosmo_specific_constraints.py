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

from base.models import CourseType, Time, Day, ScheduledCourse
from TTapp.slots import slots_filter, days_filter, slot_pause, days_list
from TTapp.TTModel import max_weight
from TTapp.iic.constraint_type import ConstraintType
from TTapp.iic.constraints.constraint import Constraint
import random

possible_tutors = {
    'Caisse' : {'Annie', 'Elsa', 'Emilie', 'Jeremy', 'Marine', 'Nicolas', 'Manon'},
    'Ménage' : {'Florian', 'Leandre', 'Pierre'},
    'Proj' : {'Adelaide', 'Annie', 'Elsa', 'Frederic', 'Jeremy', 'Nicolas', 'Manon'},
    'Autre' : {'Annie', 'Elsa', 'Emilie', 'Jeremy', 'Marine', 'Nicolas', 'Florian',
               'Leandre', 'Pierre', 'Adelaide', 'Frederic', 'Manon'}
    }

salaries = {'Manon': {'base': 35},
            'Adelaide': {'base': 28, 10: 0},
            'Frederic': {'base': 35, 9: 0},
            'Marine': {'base': 25, 3: 0, 4: 0, 5: 0, 6: 0},
            'Emilie': {'base': 15.5, 3: 33, 4: 33, 5: 33, 6: 33},
            'Nicolas': {'base': 17.5, 3: 26.5, 4: 26.5, 5: 26.5, 6: 26.5},
            'Elsa': {'base': 28},
            'Florian': {'base': 35},
            'Leandre': {'base': 35},
            'Pierre': {'base': 35},
            'Annie': {'base': 35, 8: 12},
            'Jeremy': {'base': 35}}

#temps_plein = {'Frederic',  'Manon', 'Marine', 'Elsa', 'Adelaide'}
patrons = {'Annie', 'Jeremy'}
menage = {'Florian', 'Leandre', 'Pierre'}
temps_plein = set(s for s in salaries if salaries[s]['base'] > 20) - patrons - menage
#temps_partiel = {'Emilie', 'Nicolas'
temps_partiel = set(s for s in salaries if salaries[s]['base'] <= 20) - patrons - menage
prorata = {}
for s in salaries:
    prorata[s] = salaries[s]['base'] / 35



def previous_week(week):
    previous = week - 1
    if previous == 0:
        previous = 52
    return previous


def nb_de_slots_simultanes(slot):
    if slot.start_time % 60 == 0:
        return 2
    else:
        return 1


def somme_des_cours_qui_terminent_en(ttmodel, prof, day, end_time):
    res = ttmodel.sum(ttmodel.TTinstructors[sl, c, prof]
                      for sl in ttmodel.wdb.slots if sl.end_time == end_time and sl.day==day
                      for c in ttmodel.wdb.compatible_courses[sl] & ttmodel.wdb.possible_courses[prof])
    return res


def somme_des_busy_slot_juste_apres(ttmodel, prof, day, end_time):
    res = ttmodel.sum(ttmodel.IBS[prof, sl_suivant]
                      for sl_suivant in slots_filter(ttmodel.wdb.slots, starts_after=end_time,
                                                     starts_before=end_time + slot_pause, day=day))
    return res


def add_cosmo_specific_constraints(ttmodel):
    print("Et maintenant les contraintes du Cosmo!")
    basic_cosmo_constraints(ttmodel)

    for salarie in ttmodel.wdb.instructors:
        if salarie.username not in menage:
            amplitude_max_par_jour(ttmodel, salarie)

    ttmodel.add_warning(None, "Une Coupure d'au moins 11h entre 2 jours consécutifs !")
    for salarie in ttmodel.wdb.instructors:
        coupure_nocturne_min(ttmodel, salarie, heures_coupure_min=11)

    if len(ttmodel.wdb.weeks) >= 5:
        ttmodel.add_warning(None,
                            "Au moins 2 WE pour les temps plein et 3 (ou 2 gros) pour les temps partiels")
        ttmodel.add_warning(None,
                            "Les patrons ne travaillent pas le WE (sauf si c'est forcé...)")
        #ttmodel.add_warning(None, "Maximiser les WE et quasi-WE")
        for salarie in ttmodel.wdb.instructors:
            we_cosmo_constraints(ttmodel, salarie)

    ttmodel.add_warning(None, "Pas plus de 6 jours de travail consécutifs")
    for salarie in ttmodel.wdb.instructors:
        # if salarie.username in {'Adelaide', 'Manon'}:
        #     jours_max_consecutifs(ttmodel, salarie, jours_max=5, contrainte=False)
        jours_max_consecutifs(ttmodel, salarie, jours_max=6, contrainte=True)

    ttmodel.add_warning(None, "Au moins 2/3 jours de congé par semaine")
    for salarie in ttmodel.wdb.instructors:
        if salarie.username in temps_partiel:
            jours_de_repos_par_semaine(ttmodel, salarie, jours_min=3)
        else:
            jours_de_repos_par_semaine(ttmodel, salarie, jours_min=2)

    ttmodel.add_warning(None, "Au moins 2 jours de repos consecutifs par semaine (sauf apres un WE de 3 jours")
    for salarie in ttmodel.wdb.instructors:
        deux_jours_de_repos_consecutifs(ttmodel, salarie)

    ttmodel.add_warning(None, "Les cours à suspens sont placés par blocs de 3h au moins")
    for salarie in ttmodel.wdb.instructors:
        cours_a_suspens(ttmodel, salarie, nb_heures_par_bloc=3)

    soirs_assez_longs(ttmodel, postes=ttmodel.wdb.modules.filter(abbrev__in=['Caisse', 'Proj']), limite=4)

    ttmodel.add_warning(None, "Equilibre jours/soirs : diff max de 3 par semaine et 5 globalement (dont 2 max les WE)")
    for salarie in ttmodel.wdb.instructors:
        if salarie.username not in menage:
            equilibrer_journees_et_soirees(ttmodel, salarie,
                                           diff_max_par_semaine=3,
                                           diff_max_globale=5,
                                           diff_max_we=2)
    ttmodel.add_warning(None, "Fred et Adelaïde sont principalement en proj, Elsa et Nico aussi")
    cosmo_projection_constraints(ttmodel, prioritaires={"Elsa", "Nicolas", "Frederic", "Adelaide"},
                                 super_prioritaires={"Frederic", "Adelaide"},
                                 pas_le_mercredi_AM={'Annie', 'Jeremy', 'Manon'})

    nouvelles_preferences(ttmodel)


def cosmo_projection_constraints(ttmodel, prioritaires, super_prioritaires, pas_le_mercredi_AM):
    projectionnistes_prioritaires = set(t for t in ttmodel.wdb.instructors if t.username in prioritaires)
    projectionnistes_encore_plus_prioritaires = set(t for t in ttmodel.wdb.instructors
                                                    if t.username in super_prioritaires)
    projection = ttmodel.wdb.modules.get(abbrev="Proj")
    salaries_prioritaires_sur_le_poste(ttmodel, projectionnistes_prioritaires, projection, cout=0.5)
    salaries_prioritaires_sur_le_poste(ttmodel, projectionnistes_encore_plus_prioritaires, projection, cout=0.2)
    pas_le_mercredi_matin_en_proj = set(t for t in ttmodel.wdb.instructors
                                        if t.username in pas_le_mercredi_AM)

    au_moins_une_fois_sur_le_poste(ttmodel, projectionnistes_prioritaires, projection, Day.WEDNESDAY, Time.AM)

    pas_de_cours_sur_le_poste(ttmodel, pas_le_mercredi_matin_en_proj, projection, Day.WEDNESDAY, Time.AM)

def jours_max_consecutifs(ttmodel, salarie, jours_max=6, contrainte=False):
    for day in (days_filter(ttmodel.wdb.days, week_in=ttmodel.wdb.weeks[:-1])
                | days_filter(ttmodel.wdb.days, week=ttmodel.wdb.weeks[-1], index=0)):
        local_jours_max = jours_max
        if day.week == min(ttmodel.wdb.weeks) and day.day == Day.MONDAY:
            while jours_max > 0:
                precedent = days_list[local_jours_max]
                previous_day_scheduled_courses = ScheduledCourse.objects.filter(tutor=salarie,
                                                                                course__week=previous_week(day.week),
                                                                                day=precedent, work_copy=0)
                if previous_day_scheduled_courses.exists():
                    local_jours_max -= 1
                else:
                    break
        expr = ttmodel.IBD[salarie, day]
        suivant = day
        for _ in range(local_jours_max):
            suivant = ttmodel.wdb.day_after[suivant]
            expr += ttmodel.IBD[salarie, suivant]
        if contrainte:
            ttmodel.add_constraint(expr, '<=', jours_max,
                                   Constraint(constraint_type=ConstraintType.MAX_CONSECUTIVE_DAYS,
                                              instructors=salarie, days=day)
                                   )
        else:
            ttmodel.add_to_inst_cost(salarie,
                                     ttmodel.add_floor("%s jours consécutifs après %s < %s" % (salarie.username, day,
                                                                                               jours_max),
                                                       expr, jours_max, len(ttmodel.wdb.weeks) * 7))


def jours_de_repos_par_semaine(ttmodel, salarie, jours_min=2):
    # Les temps partiels peuvent avoir trois jours de repos par semaine avec au moins deux jours consécutifs.
    # Le reste des semaines, les personnes à temps plein ont deux jours de repos par semaine
    limit = 7 - jours_min
    for week in ttmodel.wdb.weeks:
        ttmodel.add_constraint(
            ttmodel.sum(ttmodel.IBD[salarie, day] for day in days_filter(ttmodel.wdb.days, week=week)), '<=', limit,
            Constraint(constraint_type=ConstraintType.REST_DAY_BY_WEEK,
                       weeks=week, instructors=salarie))

def deux_jours_de_repos_consecutifs(ttmodel, salarie):
    for week in ttmodel.wdb.weeks:
        days = days_filter(ttmodel.wdb.days, week=week)
        expr = ttmodel.lin_expr()
        for index in range(len(days) - 1):
            jours = list(days_filter(days, index_in=[index, index + 1]))
            les_deux = ttmodel.add_var("Ni %s Ni %s_%s" % (jours[0], jours[1], salarie.username))
            ttmodel.add_constraint(les_deux + ttmodel.IBD[salarie, jours[0]] + ttmodel.IBD[salarie, jours[1]],
                                   '>=', 1,
                                   Constraint(constraint_type=ConstraintType.CONSECUTIVE_REST_DAYS,
                                              days=jours, instructors=salarie)
                                   )
            ttmodel.add_constraint(2 * les_deux + ttmodel.IBD[salarie, jours[0]] + ttmodel.IBD[salarie, jours[1]],
                                   '<=', 2, Constraint(constraint_type=ConstraintType.CONSECUTIVE_REST_DAYS,
                                                       days=jours, instructors=salarie)
                                   )
            expr += les_deux
        if ttmodel.wdb.weeks.index(week) == 0:
            ttmodel.add_constraint(expr, '>=', 1, Constraint(constraint_type=ConstraintType.CONSECUTIVE_REST_DAYS,
                                                             weeks=week, instructors=salarie)
                                   )
        else:
            ttmodel.add_constraint(expr + ttmodel.WE_3jours[salarie, previous_week(week)], '>=', 1,
                                   Constraint(constraint_type=ConstraintType.CONSECUTIVE_REST_DAYS,
                                              weeks=week, instructors=salarie))


def cours_a_suspens(ttmodel, salarie, nb_heures_par_bloc=3):
    # NB : les slots compatibles sont ceux de semaine (hors WE), de 9h à 18h
    for week in ttmodel.wdb.weeks:
        cours_a_suspens = ttmodel.wdb.courses.filter(tutor=salarie, suspens=True, week=week)
        if not cours_a_suspens.exists():
            continue
        for day in days_filter(ttmodel.wdb.days, week=week):
            nb_h_a_suspens_du_jour = ttmodel.sum(ttmodel.TTinstructors[(sl, c, salarie)] * sl.duration / 60
                                                 for sl in slots_filter(ttmodel.wdb.slots, day=day)
                                                 for c in set(cours_a_suspens) & ttmodel.wdb.compatible_courses[sl])
            # si i a des heures variables à faire, suspens est_i à 1
            # s'il est à 1, les heures à faire sont au moins à 3!
            suspens_i = ttmodel.add_var("%s fait des heures variables %s" % (salarie, day))
            card = 20
            expr = card * suspens_i - nb_h_a_suspens_du_jour
            ttmodel.add_constraint(expr, '>=', 0, Constraint(constraint_type=ConstraintType.COSMO))
            ttmodel.add_constraint(expr, '<=', card - nb_heures_par_bloc,
                                   Constraint(constraint_type=ConstraintType.COSMO))
            # Pas plus de 7 par jour
            ttmodel.add_constraint(nb_h_a_suspens_du_jour, '<=', 7,
                                   Constraint(constraint_type=ConstraintType.COSMO))


def si_module_a_alors_pas_autres_modules(ttmodel, module_a, autres_modules, salarie):
    ttmodel.add_warning(salarie, f"Si {module_a} alors pas de {autres_modules}")
    for day in ttmodel.wdb.days:
        heures_de_a = ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                                  for c in ttmodel.wdb.possible_courses[salarie] if c.module == module_a
                                  for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=day))
        heures_de_autres = ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                                       for c in ttmodel.wdb.possible_courses[salarie] if c.module in autres_modules
                                       for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=day))
        salarie_fait_du_a = ttmodel.add_floor(f"{salarie} en {module_a} {day}",heures_de_a, floor=1, bound=1000)
        ttmodel.add_constraint(1000 * salarie_fait_du_a + heures_de_autres, '<=', 1000,
                               Constraint(constraint_type=ConstraintType.IF_ONE_MODULE_THEN_NOT_OTHER_ONES,
                                          instructors=salarie,
                                          modules=list(autres_modules)+[module_a])
                               )


def soirs_assez_longs(ttmodel, postes, limite=4.5):
    ttmodel.add_warning(None, "Si on fait la fermeture le soir sur un poste, alors c'est pour 4h30 au moins,"
                              "(et pour 8h au plus...?)")
    for poste in postes:
        for day in ttmodel.wdb.days:
            if not ttmodel.wdb.sched_courses.filter(day=day.day,
                                                    course__week=day.week,
                                                    course__module=poste).exists():
                print('Pas de cours de %s %s' %(poste, day) )
                continue
            last_start_time = max(sc.start_time for sc in ttmodel.wdb.sched_courses.filter(day=day.day,
                                                                                           course__week=day.week,
                                                                                           course__module=poste))
            last_sched_course = ttmodel.wdb.sched_courses.get(day=day.day, course__week=day.week, course__module=poste,
                                                              start_time=last_start_time)
            last_course = last_sched_course.course
            end_time = last_start_time + last_course.type.duration
            slots = ttmodel.wdb.compatible_slots[last_course]
            soiree_start_time = end_time - limite * 60
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
                                               if soiree_start_time < sl.end_time
                                               for c in ttmodel.wdb.compatible_courses[sl]
                                               & ttmodel.wdb.possible_courses[i] if c.module == poste
                                               )
                                               # & ttmodel.wdb.courses.filter(module=poste))
                heures_en_tout = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                             for sl in slots_filter(ttmodel.wdb.slots, day=day)
                                             for c in ttmodel.wdb.compatible_courses[sl]
                                             & ttmodel.wdb.possible_courses[i]
                                             )
                card = 24
                expr = card * ttmodel.TTinstructors[(last_slot, last_course, i)] - heures_de_soiree
                ttmodel.add_constraint(expr, '<=', card - limite,
                                       Constraint(constraint_type=ConstraintType.LONG_EVENING, instructors=i,
                                          modules=poste, days=day)
                                       )
                # autre = heures_en_tout + card * ttmodel.TTinstructors[(last_slot, last_course, i)]
                # if i.username == 'Frederic':
                #     ttmodel.add_constraint(autre, '<=', card + 8, "%s %s ferme en %s_max" % (day, i, poste.abbrev))


def salaries_prioritaires_sur_le_poste(ttmodel, salaries_prioritaires, poste, cout=0.5):
    for salarie in salaries_prioritaires:
        heures_hors_poste = ttmodel.sum(ttmodel.TTinstructors[(sl, c, salarie)] * c.type.duration / 60
                                             for c in set(ttmodel.wdb.courses.exclude(module=poste))
                                             & ttmodel.wdb.possible_courses[salarie]
                                             for sl in ttmodel.wdb.compatible_slots[c])
        ttmodel.add_to_inst_cost(salarie,
                                 cout * heures_hors_poste)

def bosse_en_soiree_jourA_ou_jourB(ttmodel, salarie, jourA, semaineA, jourB=None, semaineB=None):
    name = f"{salarie.username} bosse en soirée le {jourA} semaine {semaineA}"
    expr = ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                       for sl in slots_filter(ttmodel.wdb.slots, week_day=jourA, week=semaineA,
                                              starts_after=20*60)
                       for c in ttmodel.wdb.possible_courses[salarie] & ttmodel.wdb.compatible_courses[sl])
    if jourB is not None:
        name += f"(ou le {jourB} semaine {semaineB})"
        expr += ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                            for sl in slots_filter(ttmodel.wdb.slots, week_day=jourB, week=semaineB,
                                                   starts_after=20*60)
                            for c in ttmodel.wdb.possible_courses[salarie] & ttmodel.wdb.compatible_courses[sl])
    ttmodel.add_constraint(expr, '>=', 1,
                           Constraint(constraint_type=ConstraintType.WORKS_ON_EVENING, instructors=salarie,
                                      days=jourA, weeks=semaineA)
                           )


def au_moins_une_fois_sur_le_poste(ttmodel, salaries, poste, jour, apm):
    for salarie in salaries:
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                                           for sl in slots_filter(ttmodel.wdb.slots, week_day=jour, apm=apm)
                                           for c in ttmodel.wdb.possible_courses[salarie]
                                           & ttmodel.wdb.compatible_courses[sl]
                                           if c.module == poste),
                               '>=',
                               1,
                               Constraint(constraint_type=ConstraintType.AT_LEAST_ONCE, instructors=salaries,
                                          modules=poste, days=jour, apm=apm)
                               )


def pas_de_cours_sur_le_poste(ttmodel, salaries_interdits, poste, jour, apm):
    ttmodel.add_constraint(ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                                       for salarie in salaries_interdits
                                       for sl in slots_filter(ttmodel.wdb.slots, week_day=jour, apm=apm)
                                       for c in ttmodel.wdb.possible_courses[salarie]
                                       & ttmodel.wdb.compatible_courses[sl]
                                       if c.module == poste),
                           '==',
                           0,
                           Constraint(constraint_type=ConstraintType.NOT_ON_THE_MODULE, instructors=salaries_interdits,
                                          modules=poste, apm=apm, days=jour)
                           )


def amplitude_max_par_jour(ttmodel, salarie, heures_amplitude_max=9):
    # Pas de journée de plus de 9h --> Inutile si "pas de trous"
    for d in ttmodel.wdb.days:
        if (salarie.username, d.day, d.week) == ('Manon', Day.TUESDAY, 10):
            continue
        for sl in slots_filter(ttmodel.wdb.slots, day=d):
            ttmodel.add_constraint(
                1000 * ttmodel.sum(ttmodel.TTinstructors[sl, c, salarie]
                         for c in ttmodel.wdb.possible_courses[salarie] & ttmodel.wdb.compatible_courses[sl])
                +
                ttmodel.sum(ttmodel.TTinstructors[sl2, c, salarie]
                            for sl2 in slots_filter(ttmodel.wdb.slots, day=d)
                            if sl2.end_time - sl.start_time > heures_amplitude_max * 60
                            for c in ttmodel.wdb.possible_courses[salarie] & ttmodel.wdb.compatible_courses[sl2]),
                '<=',
                1000,
                Constraint(constraint_type=ConstraintType.MAX_AMPLITUDE, instructors=salarie,
                           weeks=d.week, days=d.jour)
            )


def coupure_nocturne_min(ttmodel, salarie, heures_coupure_min=11):
    # Coupure de 11h au moins!
    for day in ttmodel.wdb.days:
        if day.week == max(ttmodel.wdb.weeks) and day.day == Day.SUNDAY:
            continue
        if day.week == min(ttmodel.wdb.weeks) and day.day == Day.MONDAY:
            previous_day_scheduled_courses = ScheduledCourse.objects.filter(tutor=salarie,
                                                                            course__week=previous_week(day.week),
                                                                            course__year=ttmodel.year,
                                                                            day=Day.SUNDAY, work_copy=0)
            if not previous_day_scheduled_courses.exists():
                continue
            else:
                end_previous_day = max(sc.end_time() for sc in previous_day_scheduled_courses)
                admissible_start_time = (end_previous_day + heures_coupure_min * 60) % (24*60)
                ttmodel.add_constraint(
                    ttmodel.sum(ttmodel.IBS[(salarie, sl2)]
                                for sl2 in slots_filter(ttmodel.wdb.slots, day=day,
                                                        starts_before=admissible_start_time - 1)),
                    '==',
                    0,
                    Constraint(constraint_type=ConstraintType.NIGHT_CUT, instructors=salarie,
                               days=day.day)
                    )

        successive_day = ttmodel.wdb.day_after[day]
        successive_day_slots = slots_filter(ttmodel.wdb.slots, day=successive_day)
        for sl1 in slots_filter(ttmodel.wdb.slots, day=day, starts_after=19*60):
            admissible_start_time = (sl1.end_time + heures_coupure_min*60) % (24*60)
            ttmodel.add_constraint(
                1000 * ttmodel.IBS[(salarie, sl1)] +
                ttmodel.sum(ttmodel.IBS[(salarie, sl2)] for sl2 in successive_day_slots
                            if sl2.start_time < admissible_start_time),
                '<=',
                1000,
                Constraint(constraint_type=ConstraintType.NIGHT_CUT, instructors=salarie,
                           slots=sl1)
            )


def we_cosmo_constraints(ttmodel, salarie):
    # sur 5 semaines, pendant lesquelles chaque personne a
    # un week-end de trois jours de repos (samedi dimanche lundi)
    #       + un jour de week-end la semaine suivante (samedi ou dimanche).
    # (qu'on essaie d'être le plus régulier possible).
    jours_de_WE = days_filter(ttmodel.wdb.days, index_in=[5, 6])

    if salarie.username not in menage:
        # somme_de_we compte donc 1 par quasiWE, 2 par WE et 3 par WE_3jours...
        somme_de_we = ttmodel.sum(ttmodel.quasiWE[salarie, week] for week in ttmodel.wdb.weeks) + \
                      ttmodel.sum(ttmodel.WE[salarie, week] for week in ttmodel.wdb.weeks) + \
                      ttmodel.sum(ttmodel.WE_3jours[salarie, week] for week in ttmodel.wdb.weeks)

        # ttmodel.add_constraint(ttmodel.sum(ttmodel.WE_3jours[salarie, week] for week in ttmodel.wdb.weeks),
        #                        '>=',
        #                        1,
        #                        "Au moins 1 WE de 3 jours pour %s" % salarie.username)
        # ttmodel.add_constraint(ttmodel.sum(ttmodel.IBD[salarie, jour] for jour in jours_de_WE),
        #                        '<=',
        #                        7,
        #                        "Au moins 3 jours de WE %s" % salarie.username)
        if salarie.username in temps_plein:
            ttmodel.add_constraint(somme_de_we,
                                   '>=',
                                   4,
                                   Constraint(constraint_type=ConstraintType.COSMO_WE, instructors=salarie)
                                   )
            if ttmodel.deux_we:
                ttmodel.add_constraint(ttmodel.sum(ttmodel.WE[salarie, week] for week in ttmodel.wdb.weeks),
                                       '>=',
                                       2,
                                       Constraint(constraint_type=ConstraintType.COSMO_WE, instructors=salarie)
                                       )
                # else:
            #     ttmodel.add_constraint(ttmodel.sum(ttmodel.quasiWE[salarie, week] for week in ttmodel.wdb.weeks),
            #                            '>=',
            #                            2,
            #                            "au moins 2 quasi WE pour %s" % salarie.username)
        if salarie.username in temps_partiel | patrons:
            ttmodel.add_constraint(somme_de_we,
                                   '>=',
                                   5,
                                   Constraint(constraint_type=ConstraintType.COSMO_WE, instructors=salarie)
                                   )
            # if ttmodel.deux_we:
            #     ttmodel.add_constraint(ttmodel.sum(ttmodel.WE[salarie, week] for week in ttmodel.wdb.weeks),
            #                            '>=',
            #                            3,
            #                            "au moins 3 WE pour %s" % salarie.username)
            # else:
            #     ttmodel.add_constraint(ttmodel.sum(ttmodel.WE[salarie, week] for week in ttmodel.wdb.weeks),
            #                            '>=',
            #                            2,
            #                            "au moins 2 WE pour %s" % salarie.username)
            #     ttmodel.add_constraint(ttmodel.sum(ttmodel.quasiWE[salarie, week] for week in ttmodel.wdb.weeks),
            #                            '>=',
            #                            3,
            #                            "au moins 3 quasi WE pour %s" % salarie.username)
        # if salarie.username not in patrons:
        #     ttmodel.add_constraint(ttmodel.sum(ttmodel.quasiWE[salarie, week] for week in ttmodel.wdb.weeks),
        #                            '<=',
        #                            3,
        #                            "Pas plus de 3 quasi-WE pour %s" % salarie.username)

        # ttmodel.add_to_inst_cost(salarie, -5 * ttmodel.sum(ttmodel.quasiWE[salarie, week]
        #                                                    for week in ttmodel.wdb.weeks))
        # ttmodel.add_to_inst_cost(salarie, -5 * ttmodel.sum(ttmodel.WE[salarie, week]
        #                                                    + 0.5 * ttmodel.WE_3jours[salarie, week]
        #                                                    for week in ttmodel.wdb.weeks))

    # Les patrons peuvent travailler le WE, mais le coût a été rendu très grand...
    if salarie.username in patrons:
        # ttmodel.add_constraint(ttmodel.sum(ttmodel.IBD[salarie, d] - ttmodel.forced_IBD[salarie, d] * ttmodel.UN
        #                                    for d in jours_de_WE),
        #                        '==',
        #                        0,
        #                        "Pas de travail le WE - %s" % salarie.username)
        for week in ttmodel.weeks:
            WE = days_filter(jours_de_WE, week=week)
            ttmodel.add_to_inst_cost(salarie,
                                     ttmodel.sum(ttmodel.IBD[salarie, d] - ttmodel.forced_IBD[salarie, d] * ttmodel.UN
                                                 for d in WE) * 100,
                                     week=week)


def basic_cosmo_constraints(ttmodel):
    projection = ttmodel.wdb.modules.get(abbrev="Proj")
    autre = ttmodel.wdb.modules.get(abbrev="Autre")
    controle = ttmodel.wdb.modules.get(abbrev="Ct_Men")

    reus_d_equipe = [(8, Day.TUESDAY)]
    for reu in reus_d_equipe:
        if reu[0] in ttmodel.weeks:
            for prenom in salaries:
                if reu[0] in salaries[prenom]:
                    if salaries[prenom][reu[0]] >= 2.5:
                        salaries[prenom][reu[0]] -= 2.5
                else:
                    salaries[prenom][reu[0]] = salaries[prenom]['base'] - 2.5
            # print("On a changé le nombre d'heures pour le réu d'équipe
            # semaine %s (%s dans le tableau)" % (reu[0], reu[0]-ttmodel.wdb.weeks[0]))

    heures_max = {week: {} for week in ttmodel.wdb.weeks}
    heures_max['jour'] = {}
    heures_min = {week: {} for week in ttmodel.wdb.weeks}
    heures_min['jour'] = {}

    for week in ttmodel.wdb.weeks:
        for i in ttmodel.wdb.instructors:
            if i.username not in salaries:
                continue
            username = i.username
            heures_max['jour'][username] = i.max_hours_per_day
            heures_min['jour'][username] = 0
            if week in salaries[username]:
                heures_hebdo = salaries[username][week]
            else:
                heures_hebdo = salaries[username]['base']
            if username in menage:
                heures_min[week][username] = 0
                heures_max[week][username] = 40
            elif username in patrons:
                heures_min[week][username] = 0
                heures_max[week][username] = heures_hebdo
            else:
                heures_min[week][username] = heures_hebdo - 5 * prorata[username] if heures_hebdo != 0 else 0
                heures_max[week][username] = heures_hebdo + 8 * prorata[username] if heures_hebdo != 0 else 0
                if username in ['Manon', 'Nicolas']:
                    heures_min['jour'][username] = 5
                elif username == "Adelaide":
                    heures_min['jour'][username] = 6
                else:
                    heures_min['jour'][username] = 4

    heures_periode = {}
    for i in ttmodel.wdb.instructors:
        heures_periode[i] = sum(salaries[i.username][week] if week in salaries[i.username]
                                else salaries[i.username]['base']
                                for week in ttmodel.weeks)
    for i in ttmodel.wdb.instructors:
        if i.username in menage or i.username not in salaries:
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
                                   Constraint(constraint_type=ConstraintType.MAX_HOURS, instructors=i,
                                              weeks=week)
                                   )
            ttmodel.add_constraint(ttmodel.nb_heures[i][week],
                                   '>=',
                                   heures_min[week][i.username],
                                   Constraint(constraint_type=ConstraintType.MIN_HOURS, instructors=i,
                                              weeks=week)
                                   )
        ttmodel.nb_heures[i]['total'] = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                                    for sl in ttmodel.wdb.slots
                                                    for c in set(ttmodel.wdb.possible_courses[i]) &
                                                    ttmodel.wdb.compatible_courses[sl])

        if i.username not in patrons | menage:
            if i.username in temps_plein:
                limit = 3
            else:
                limit = 5
            ttmodel.add_constraint(ttmodel.nb_heures[i]['total'],
                                   '<=',
                                   heures_periode[i] + limit * prorata[i.username],
                                   Constraint(constraint_type=ConstraintType.DO_NOT_WORK_TOO_MUCH, instructors=i)
                                   )
            ttmodel.add_constraint(ttmodel.nb_heures[i]['total'],
                                   '>=',
                                   heures_periode[i] - limit * prorata[i.username],
                                   Constraint(constraint_type=ConstraintType.WORKS_ENOUGH, instructors=i)
                                   )
        # Respecte les limites par jour
        for day in ttmodel.wdb.days:
            ttmodel.nb_heures[i][day] = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)]*sl.duration/60
                                         for sl in slots_filter(ttmodel.wdb.slots, day=day)
                                         for c in set(ttmodel.wdb.possible_courses[i]) & ttmodel.wdb.compatible_courses[sl])

            ttmodel.add_constraint(ttmodel.nb_heures[i][day],
                                   '<=',
                                   heures_max['jour'][i.username],
                                   Constraint(constraint_type=ConstraintType.DO_NOT_WORK_TOO_MUCH, instructors=i,
                                              days=day)
                                   )
            #if not ttmodel.forced_IBD[i, day]:
            if (day.week, day.day) not in reus_d_equipe:
                ttmodel.add_constraint(heures_min['jour'][i.username] * ttmodel.IBD[(i, day)] -
                                       ttmodel.nb_heures[i][day],
                                       '<=',
                                       0,
                                       Constraint(constraint_type=ConstraintType.WORKS_ENOUGH,
                                                  instructors=i, days=day)
                                       )

                # else:
            #     print("réu d'équipe pour %s le %s" % (i, day))
    ttmodel.nb_heures['total'] = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)] * sl.duration / 60
                                             for sl in ttmodel.wdb.slots
                                             for i in ttmodel.wdb.instructors if i.username in temps_partiel
                                                                                               | temps_plein
                                             for c in set(ttmodel.wdb.possible_courses[i]) &
                                             ttmodel.wdb.compatible_courses[sl])
    heures_periode['total'] = sum(heures_periode[i] for i in ttmodel.wdb.instructors
                                  if i.username in temps_partiel | temps_plein)

    ttmodel.add_constraint(ttmodel.nb_heures['total'],
                           '>=',
                           heures_periode['total'] - 2 * len(temps_plein | temps_partiel),
                           Constraint(constraint_type=ConstraintType.DO_NOT_WORK_TOO_MUCH)
                           )

    ttmodel.Module_per_day = {}
    for i in ttmodel.wdb.instructors:
        for m in ttmodel.wdb.possible_modules[i]:
            ttmodel.Module_per_day[(i, m)] = {}
            for d in ttmodel.wdb.days:
                ttmodel.Module_per_day[(i, m)][d] = ttmodel.add_var("Mod_per_day(%s,%s,%s)" % (i, m, d))
                # Linking the variable to the TT
                dayslots = slots_filter(ttmodel.wdb.slots, day=d)
                card = 2 * len(dayslots)
                expr = ttmodel.lin_expr()
                expr += card * ttmodel.Module_per_day[(i, m)][d]
                for c in set(ttmodel.wdb.courses.filter(module=m)) & ttmodel.wdb.possible_courses[i]:
                    for sl in dayslots & ttmodel.wdb.compatible_slots[c]:
                        expr -= ttmodel.TTinstructors[(sl, c, i)]
                ttmodel.add_constraint(expr, '>=', 0,
                                       Constraint(constraint_type=ConstraintType.MAX_MODULES_PER_DAY,
                                                  instructors=i, days=d, modules=m)
                                       )

    # Two module max per day : (1 Enlevé pour passer de la caisse au contrôle)
    exceptions = [('Nicolas', 2, Day.THURSDAY ), ('Nicolas', 2, Day.FRIDAY)]

    for d in ttmodel.wdb.days:
        for i in ttmodel.wdb.instructors:
            limit = 2
            if (i.username, d.week, d.day) in exceptions:
                limit = 3
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.Module_per_day[(i, m)][d] for m in ttmodel.wdb.possible_modules[i]),
                '<=',
                limit,
                Constraint(constraint_type=ConstraintType.MAX_MODULES_PER_DAY,
                           instructors=i, days=d)
            )

    heures_par_jour = {}
    amplitude = {}
    for mod in ttmodel.wdb.modules:
        for d in ttmodel.wdb.days:
            SC = ttmodel.wdb.sched_courses.filter(course__week=d.week, day=d.day, course__module=mod)\
                                          .exclude(course__tutor__username__in=menage)
            heures_par_jour[(mod, d)] = sum(sc.course.type.duration for sc in SC)/60
            if SC.exists():
                amplitude[(mod, d)] = (max(sc.start_time + sc.course.type.duration for sc in SC)
                                       - min(sc.start_time for sc in SC))/60
            else:
                amplitude[(mod, d)] = 0

    # One or two tutors max per day
    ttmodel.add_warning(None, "<9h: Un seul salarié. >9h: Pas plus de 2 salariés par jour sur un même poste")
    for m in ttmodel.wdb.modules:
        if m.abbrev == 'Autre':
            continue
        g = ttmodel.wdb.groups.get(name=m.abbrev)
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
                - limit * ttmodel.UN
            #ttmodel.add_to_group_cost(g, cost)
            ttmodel.add_constraint(cost, '<=', 0,
                                   Constraint(constraint_type=ConstraintType.MAX_TUTORS_PER_DAY,
                                              days=d, modules=m)
                                   )

    fin_de_bloc = {}
    nb_trous = {}

    for i in ttmodel.wdb.instructors:
        for d in ttmodel.wdb.days:
            possible_end_times = list(set(sl.end_time for sl in slots_filter(ttmodel.wdb.slots, day=d)))
            possible_end_times.sort()
            for end_time in possible_end_times:
                fin_de_bloc[i, end_time] = ttmodel.add_var("%s a un bloc qui finit a %gh" % (i.username, end_time/60))
                # Si c'est une fin de bloc, un cours se termine là
                ttmodel.add_constraint(
                    fin_de_bloc[i, end_time] - somme_des_cours_qui_terminent_en(ttmodel, i, d, end_time),
                    '<=', 0,
                    Constraint(constraint_type=ConstraintType.HOLES,
                               days=d, instructors=i)
                    )
                # si c'est une fin de bloc, y'a pas de busy_slot juste après
                ttmodel.add_constraint(
                    somme_des_busy_slot_juste_apres(ttmodel, i, d, end_time)
                    + 100 * fin_de_bloc[i, end_time], '<=', 100,
                    Constraint(constraint_type=ConstraintType.HOLES,
                               days=d, instructors=i)
                    )
                # si c'est pas une fin de bloc, y'en a juste après OU y'en a pas qui se terminent là
                ttmodel.add_constraint(
                    somme_des_busy_slot_juste_apres(ttmodel, i, d, end_time)
                    + (ttmodel.UN - somme_des_cours_qui_terminent_en(ttmodel, i, d, end_time))
                    + fin_de_bloc[i, end_time], '>=', 1,
                    Constraint(constraint_type=ConstraintType.HOLES,
                               days=d, instructors=i)
                    )

            nb_trous[i, d] = ttmodel.sum(fin_de_bloc[i, end_time]
                                         for end_time in possible_end_times) - ttmodel.IBD[i, d]

    for d in ttmodel.wdb.days:
        diff_proj = amplitude[projection, d] - heures_par_jour[projection, d]
        diff_autre = amplitude[autre, d] - heures_par_jour[autre, d]
        diff_controle = amplitude[controle, d] - heures_par_jour[controle, d]
        trouEs_autre = set()
        trouEs_controle = set()
        trouEs_proj = set()
        if diff_proj >= 1:
            possible_proj = list(possible_tutors['Proj'] - patrons - {'Manon'})
            green_possible_proj = [l for l in possible_proj if (ttmodel.unp_slot_cost[l][sl] == 0
                                                                for sl in slots_filter(ttmodel.wdb.slots, day=d))]
            if green_possible_proj:
                random_proj = random.choice(green_possible_proj)
                green = True
            else:
                random_proj = random.choice(possible_proj)
                green = False
            # print(random_proj)
            pas_de_chance_set = set(t for t in ttmodel.wdb.instructors
                                    if t.username == random_proj)
            # print(pas_de_chance_set)
            pas_de_chance = pas_de_chance_set.pop()
            trouEs_proj.add(pas_de_chance)
            print(f"{d}: trou imposé en proj à {pas_de_chance.username} {'(pas de chance)' if not green else ''}...")
        if diff_autre >= 1:
            for c in ttmodel.wdb.sched_courses.filter(day=d.day, course__week=d.week, course__module=autre)\
                    .exclude(course__tutor=None).exclude(course__tutor__username__in=menage):
                trouEs_autre.add(c.tutor)
            if len(trouEs_autre) > 1:
                trouEs_autre = set()
            if trouEs_autre:
                print(d, ": trou imposé en Autre...", trouEs_autre)
        if diff_controle >= 1:
            for c in ttmodel.wdb.sched_courses.filter(day=d.day, course__week=d.week, course__module=controle)\
                    .exclude(course__tutor=None).exclude(course__tutor__username__in=menage):
                trouEs_controle.add(c.tutor)
            if len(trouEs_controle) > 1:
                trouEs_controle = set()
            if trouEs_controle:
                print(d, ": trou imposé en Controle...", trouEs_controle)
        for i in ttmodel.wdb.instructors:
            if i.username in menage:
                continue
            if i in trouEs_controle | trouEs_autre | trouEs_proj:
                trous_max = 1
            elif (i.username, d.day, d.week) == ('Manon', Day.TUESDAY, 10):
                trous_max = 1
            else:
                trous_max = 0
            ttmodel.add_constraint(nb_trous[i, d], '<=', trous_max,
                                   Constraint(constraint_type=ConstraintType.HOLES,
                                              days=d, instructors=i)
                                   )
            # Attention, cette minimisation du nombre de trous vient en contradiction
            # avec l'espoir que IBD se définisse par minimisation ...
            # if (d.week, d.day) not in reus_d_equipe:
            #     ttmodel.add_to_inst_cost(i, 10 * nb_trous[i, d])
            # else:
            #     ttmodel.add_to_inst_cost(i, 10 * (nb_trous[i, d]) + ttmodel.IBD[i, d]))

    # Ménage:
    ttmodel.add_constraint(
        ttmodel.sum(ttmodel.TTinstructors[sl, c, i]
                    for i in ttmodel.wdb.instructors if i.username in menage
                    for c in ttmodel.wdb.possible_courses[i] if c.tutor is None
                    for sl in ttmodel.wdb.compatible_slots[c]),
        '==',
        0,
        Constraint(constraint_type=ConstraintType.COSMO)
    )

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

    # Semaine 4, peu d'heures patrons, et au pire en proj!
    if len(ttmodel.wdb.weeks) >= 5:
        avant_derniere_semaine = ttmodel.wdb.weeks[-2]
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TTinstructors[sl, c, i]
                                           for sl in slots_filter(ttmodel.wdb.slots,
                                                                  week=avant_derniere_semaine)
                                           for i in ttmodel.wdb.instructors if i.username in patrons
                                           for c in ttmodel.wdb.compatible_courses[sl] & ttmodel.wdb.possible_courses[i]
                                           if c.tutor != i and c.module != projection),
                               '==', 0,
                               Constraint(constraint_type=ConstraintType.COSMO)
                               )

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


    diff_max_entre_patrons_par_semaine = 7
    ttmodel.add_warning(None, "Max %d heures par semaine de différence entre les patrons"
                        % diff_max_entre_patrons_par_semaine)
    Annie = Jeremy = None
    for i in ttmodel.wdb.instructors:
        if i.username == 'Annie':
            Annie = i
        elif i.username == 'Jeremy':
            Jeremy = i
    for semaine in ttmodel.wdb.weeks:
        if semaine in salaries['Annie'] or semaine in salaries['Jeremy']:
            continue
        ttmodel.add_constraint(heures_reelles_hebdo[semaine][Annie] - heures_reelles_hebdo[semaine][Jeremy],
                               '<=', diff_max_entre_patrons_par_semaine,
                               Constraint(constraint_type=ConstraintType.COSMO,
                                          weeks=semaine, instructors=[Annie, Jeremy])
                               )
        ttmodel.add_constraint(heures_reelles_hebdo[semaine][Jeremy] - heures_reelles_hebdo[semaine][Annie],
                               '<=', diff_max_entre_patrons_par_semaine,
                               Constraint(constraint_type=ConstraintType.COSMO,
                                          weeks=semaine, instructors=[Annie, Jeremy])
                               )
    

    ttmodel.add_warning(None, "Eviter que les boss bossent, et surtout pas les deux boss bossent le même jour")

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
    # (Si ça ne dépasse pas la borne posée dans pref_hours_per_day)
    for salarie in ttmodel.wdb.instructors:
        if salarie.username not in salaries:
            continue
        for semaine in ttmodel.wdb.weeks:
            cout_jours_de_trop = 0
            # need to be sorted
            frontier_pref_busy_days = [salarie.pref_hours_per_day * d for d in range(6, 0, -1)]
            if semaine in salaries[salarie.username]:
                nb_heures_a_faire = salaries[salarie.username][semaine]
            else:
                nb_heures_a_faire = salaries[salarie.username]['base']
            nb_days = 7

            for fr in frontier_pref_busy_days:
                if nb_heures_a_faire <= fr:
                    cout_jours_de_trop += ttmodel.IBD_GTE[semaine][nb_days][salarie]
                    nb_days -= 1
                else:
                    break
            ttmodel.add_to_inst_cost(salarie, ttmodel.min_bd_i * cout_jours_de_trop, week=semaine)

    for reu in reus_d_equipe:
        if reu[0] in ttmodel.wdb.weeks:
            jour = days_filter(ttmodel.wdb.days, week=reu[0], day=reu[1]).pop()
            for salarie in ttmodel.wdb.instructors:
                if salarie.username in salaries:
                    ttmodel.add_constraint(ttmodel.IBD[salarie, jour], '==', 1,
                                           Constraint(constraint_type=ConstraintType.COSMO,
                                                      days=jour, instructors=salarie)
                    )


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


def equilibre_dans_les_deux_sens(ttmodel, valeur, salarie, attribut1, attribut2=None):
    a = ttmodel.soirs_travailles[salarie][attribut1]
    b = ttmodel.jours_travailles[salarie][attribut1]
    if attribut2 is not None:
        a = a[attribut2]
        b = b[attribut2]
    ttmodel.add_constraint(a-b, '<=', valeur, Constraint(constraint_type=ConstraintType.BALANCE))
    ttmodel.add_constraint(b-a, '<=', valeur, Constraint(constraint_type=ConstraintType.BALANCE))


def equilibrer_journees_et_soirees(ttmodel, salarie, diff_max_par_semaine, diff_max_globale, diff_max_we=2):
    for week in ttmodel.wdb.weeks:
        equilibre_dans_les_deux_sens(ttmodel, diff_max_par_semaine, salarie, week)
    equilibre_dans_les_deux_sens(ttmodel, diff_max_globale, salarie, 'TOTAL', 'semaine')
    equilibre_dans_les_deux_sens(ttmodel, diff_max_we, salarie, 'TOTAL', 'WE')
    # for week in ttmodel.wdb.weeks:
    #     ttmodel.add_constraint(ttmodel.soirs_travailles[salarie][week] - ttmodel.jours_travailles[salarie][week],
    #                            '<=', diff_max_par_semaine)
    #     ttmodel.add_constraint(ttmodel.jours_travailles[salarie][week] - ttmodel.soirs_travailles[salarie][week],
    #                            '<=', diff_max_par_semaine)
    # ttmodel.add_constraint(ttmodel.soirs_travailles[salarie]['TOTAL']['semaine'] -
    #                        ttmodel.jours_travailles[salarie]['TOTAL']['semaine'],
    #                        '<=', diff_max_globale)
    # ttmodel.add_constraint(ttmodel.soirs_travailles[salarie]['TOTAL']['WE'] -
    #                        ttmodel.jours_travailles[salarie]['TOTAL']['WE'],
    #                        '<=', diff_max_we)



def nouvelles_preferences(ttmodel):
    Marine = set(t for t in ttmodel.wdb.instructors if t.username == "Marine").pop()
    Emilie = set(t for t in ttmodel.wdb.instructors if t.username == "Emilie").pop()
    Elsa = set(t for t in ttmodel.wdb.instructors if t.username == "Elsa").pop()
    si_module_a_alors_pas_autres_modules(ttmodel, ttmodel.wdb.modules.get(abbrev="Autre"),
                                             ttmodel.wdb.modules.exclude(abbrev='Autre'), Marine)

    bosse_en_soiree_jourA_ou_jourB(ttmodel, Emilie, 'm', ttmodel.weeks[-2])
    bosse_en_soiree_jourA_ou_jourB(ttmodel, Emilie, 'tu', ttmodel.weeks[-2], 'f', ttmodel.weeks[-3])

    bosse_en_soiree_jourA_ou_jourB(ttmodel, Elsa, 's', ttmodel.weeks[-2])
    bosse_en_soiree_jourA_ou_jourB(ttmodel, Elsa, 'm', ttmodel.weeks[-1])
    # 1. Au consensus unanime:
        # OK 2 week-ends par fanzine (repos du vendredi 17h au dimanche minuit inclus)
        # OK équilibrer le nombre de soirées et de journées
    # 2. Recueil des attentes particulières (sans ordre d’importance):
        # OK avoir les jours de repos consécutifs (Elsa, Fred, Manon, Marine, Nicolas)
        # - ne pas travailler de 15h à minuit, idéalement à partir de 16h surtout le week-end (Fred)
        # WEB-OK amplitude horaire journalière max 9h et min 4h (Émilie)
        # WEB-OK amplitude horaire journalière max 8h et min 6h (Adélaïde)
        # WEB-OK amplitude horaire journalière max 9h et min 5h (Manon, Nicolas)
        # WEB préférence pour les grosses journées (Elsa, Manon)
        # OK ne pas travailler plus de 5 jours d’affilé (Adélaïde, Manon)
        # - les jours de réunions, attention à ce que les personnes ne fassent pas
        # 15h-00h00 (général sauf Elsa et Nicolas)
        # - libérer plusieurs heures hors caisse pour avancer sur nos tâches spécifiques
        # (Émilie, Marine)
        # (Refusé) avoir 2 jours en projections/semaine (Manon)
        # - maximum 3 jours de travail par semaine, consécutifs autant que possible
        # (Émilie, Nicolas)
        # - le plus possible de jours consécutifs de repos d'une semaine à l'autre (ex du
        # vendredi au mercredi suivant 1 semaine sur 2 (Nicolas)
        # - 3 week-ends off par planning, au minimum 2 week-ends et demi (Émilie)
        # (???) ne pas faire dans la même journée le ménage & le contrôle (Florian, Océane)
        # - temps de pause: une heure max

    # 3. Commentaires du 19/12:
    # - pour les WE, on peut dire un WE de 3 jours si un seul WE, sinon, 2 WE de 2 jours
    #       -> s'ils arrivent à avoir 2 WE, ils ne demandent plus nécessairement 3 jours
    # OK!
    # - Fred, Adélaïde, Nicolas et Elsa sont principalement en proj, mais dans le cas où Fred ou Adéle
    # travaillent avec Nicolas ou Elsa, c'est Fred ou Adèle en projection et Nicolas ou Elsa en caisse.
    # - est-ce qu'on pourrait coder quelque chose qui dirait de tendre le plus possible vers le fait que
    # sur les 5 (ou 6) semaines ils fassent la totalité de leurs heures
    # - prendre en compte les diff jours/soirs d'un planning sur l'autre