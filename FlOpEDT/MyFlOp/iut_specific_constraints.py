# coding:utf-8

# !/usr/bin/python

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


from TTapp.models import LimitCourseTypeTimePerPeriod, ReasonableDays, MinHalfDays, max_weight, \
    SimultaneousCourses, LimitedStartTimeChoices, LimitedRoomChoices, slots_filter, days_filter
from base.models import Time, Day, TrainingProgramme, CourseType, Module, RoomGroup, Department, ScheduledCourse
from people.models import Tutor, SupplyStaff


def add_iut_specific_constraints(ttmodel):
    add_iut_blagnac_basics(ttmodel)
    add_iut_blagnac_specials(ttmodel)
    if ttmodel.department.abbrev == 'INFO':
        add_iut_blagnac_lp(ttmodel)
        add_iut_blagnac_info(ttmodel)
    elif ttmodel.department.abbrev == 'RT':
        add_iut_blagnac_rt(ttmodel)
    elif ttmodel.department.abbrev == 'GIM':
        add_iut_blagnac_gim(ttmodel)
    elif ttmodel.department.abbrev == 'CS':
        add_iut_blagnac_cs(ttmodel)


def minimize_busy_days(ttmodel, week, tutor, cost):
    """
    Minimize the number of busy days for tutor with cost
    (if it does not overcome the bound expressed in pref_hours_per_day)
    """
    slot_by_day_cost = 0
    # need to be sorted
    courses_hours = sum(c.type.duration
                        for c in ttmodel.wdb.courses_for_tutor[tutor] & ttmodel.wdb.courses_by_week[week]) / 60
    nb_days = 5
    frontier_pref_busy_days = [tutor.pref_hours_per_day * d for d in range(nb_days - 1, 0, -1)]

    for fr in frontier_pref_busy_days:
        if courses_hours <= fr:
            slot_by_day_cost += ttmodel.IBD_GTE[week][nb_days][tutor]
            nb_days -= 1
        else:
            break
    ttmodel.add_to_inst_cost(tutor, cost * slot_by_day_cost, week=week)


def bound_hours_per_day(ttmodel, week, tutor):
    """
    respect max_hours_per_days bound
    """
    for d in days_filter(ttmodel.wdb.days, week=week):
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] * c.type.duration / 60
                                           for c in ttmodel.wdb.courses_for_tutor[tutor] if c.week == week
                                           for sl in slots_filter(ttmodel.wdb.slots, day=d)
                                           & ttmodel.wdb.compatible_slots[c]),
                               '<=',
                               tutor.max_hours_per_day,
                               constraint_type="bound hours per day", instructor=tutor, days=d)


def add_iut_blagnac_basics(ttmodel):
    print("adding IUT Blagnac's basic constraints")

    # Libérer des demi-journées aux étudiants
    M = MinHalfDays(weight=max_weight)
    M.save()
    for g in ttmodel.wdb.basic_groups.exclude(train_prog__abbrev='APSIO'):
        M.groups.add(g)
    M.save()
    for week in ttmodel.weeks:
        M.enrich_model(ttmodel, week, ttmodel.min_bhd_g)
    M.delete()
    # Minimize the number of busy days
    for week in ttmodel.wdb.weeks:
        for i in ttmodel.wdb.instructors:
            minimize_busy_days(ttmodel, week, i, ttmodel.min_bd_i)

    exceptions_bound_hours_per_day = [(46, 'MN')]

    for i in ttmodel.wdb.instructors:
        for week in ttmodel.wdb.weeks:
            if (week, i.username) not in exceptions_bound_hours_per_day:
                bound_hours_per_day(ttmodel, week, i)
            else:
                ttmodel.add_warning(i, "No bound on hours per day week %g!" % week)


def add_iut_blagnac_specials(ttmodel):
    print("adding IUT Blagnac's special constraints")
    CM = CourseType.objects.get(name='CM', department=ttmodel.department)
    if ttmodel.department.abbrev == 'INFO':
        DS = CourseType.objects.get(name='DS', department=ttmodel.department)
    elif ttmodel.department.abbrev == 'RT':
        DS = CourseType.objects.get(name='Examen', department=ttmodel.department)
    elif ttmodel.department.abbrev == 'GIM':
        DS = CourseType.objects.get(name='CTRL', department=ttmodel.department)
    elif ttmodel.department.abbrev == 'CS':
        DS = CourseType.objects.get(name='Exam', department=ttmodel.department)
    # Pas de cours le jeudi après-midi (sauf pour la LP APSIO)
    pas_jeudi_PM = ttmodel.wdb.courses.exclude(group__train_prog__abbrev__in=['APSIO', 'RT2A'])
    pas_jeudi_PM = pas_jeudi_PM.exclude(tutor__username__in=['JLF', 'JCA'])
    ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[(sl, c)]
                                       for c in pas_jeudi_PM
                                       for sl in slots_filter(ttmodel.wdb.slots, week_day=Day.THURSDAY, apm=Time.PM)
                                       & ttmodel.wdb.compatible_slots[c]),
                           '==', 0, constraint_type="Pas_de_cours_le_jeudi_aprem")

    # Pas plus de 2 examens par jour!
    pas_plus_de_2_exams_par_jour = True
    if pas_plus_de_2_exams_par_jour:
        for promo in ttmodel.train_prog:
            L = LimitCourseTypeTimePerPeriod(max_hours=3,
                                             course_type=DS,
                                             period=LimitCourseTypeTimePerPeriod.FULL_DAY,
                                             train_prog=promo)
            L.save()
            for week in ttmodel.weeks:
                L.enrich_model(ttmodel, week)
            L.delete()

    # Pas plus de 2 amphis par demie journée
    pas_plus_de_2_amphis_par_demi_journee = True
    if 36 in ttmodel.weeks:
        pas_plus_de_2_amphis_par_demi_journee = False
    if pas_plus_de_2_amphis_par_demi_journee:
        for promo in ttmodel.train_prog:
            L = LimitCourseTypeTimePerPeriod(max_hours=3,
                                             course_type=CM,
                                             period=LimitCourseTypeTimePerPeriod.HALF_DAY,
                                             train_prog=promo)
            L.save()
            for week in ttmodel.weeks:
                L.enrich_model(ttmodel, week)
            L.delete()

    # Pas plus d'un amphi par matière et par jour
    un_amphi_par_matiere_par_jour = True
    if ttmodel.department.abbrev in ['RT', 'CS', 'GIM']:
        un_amphi_par_matiere_par_jour = False
    if un_amphi_par_matiere_par_jour:
        for module in ttmodel.wdb.modules:
            L = LimitCourseTypeTimePerPeriod(max_hours=2,
                                             course_type=CM,
                                             period=LimitCourseTypeTimePerPeriod.FULL_DAY,
                                             module=module)
            L.save()
            for week in ttmodel.weeks:
                L.enrich_model(ttmodel, week)
            L.delete()

    promos1 = ttmodel.wdb.train_prog.filter(abbrev__in=['RT1', 'GIM1', 'CS1', 'INFO1'])

    sports = ttmodel.wdb.modules.filter(abbrev='SC', train_prog__in=promos1)
    for sport in sports:
        cours_de_sport = set(ttmodel.wdb.courses.filter(module=sport))
        if not cours_de_sport:
            continue
        # C, created = LimitedStartTimeChoices.objects.get_or_create(module=sport)
        # if created:
        #     C.save()
        #     C.possible_start_times.add(17*60+15)
        #     C.save()
        # C.enrich_model(ttmodel)
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                           for sl in set(slot for slot in ttmodel.wdb.slots
                                                         if not (slot.day.day in [Day.MONDAY, Day.TUESDAY]
                                                                 and slot.start_time == 17 * 60 + 15))
                                           for c in cours_de_sport & ttmodel.wdb.compatible_courses[sl]
                                           ),
                               "==",
                               0,
                               constraint_type="pas de sport sauf lundi et mardi", module=sport)

    if promos1.exists():
        if not ttmodel.department.abbrev == 'RT':
            ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                               for sl in ttmodel.wdb.slots
                                               if sl.end_time > 17 * 60 + 15 and sl.day in [Day.MONDAY, Day.TUESDAY]
                                               for c in set(ttmodel.wdb.courses.filter(group__train_prog__in=promos1)
                                                            .exclude(module__abbrev='SC'))
                                               & ttmodel.wdb.compatible_courses[sl]),
                                   '==',
                                   0, constraint_type="pas de cours de promo1 sur un creneau de sport")
        else:
            for sl in ttmodel.wdb.slots:
                if sl.end_time > 17 * 60 + 15 and sl.day in [Day.MONDAY, Day.TUESDAY]:
                    ttmodel.add_to_slot_cost(sl, 10000 * ttmodel.sum(ttmodel.TT[sl, c]
                                                                     for c in set(ttmodel.wdb.courses.
                                                                                  filter(group__train_prog__in=promos1)
                                                                                  .exclude(module__abbrev='SC'))
                                                                     & ttmodel.wdb.compatible_courses[sl]))

    if 41 in ttmodel.weeks and ttmodel.department.abbrev in ['RT', 'INFO']:
        C = ttmodel.wdb.courses.filter(group__train_prog__abbrev__in=['INFO2', 'RT2', 'RT2A', 'APSIO']) \
            .exclude(module__abbrev='CONF')
        mardi_11h = slots_filter(ttmodel.wdb.slots, week_day=Day.TUESDAY, start_time=11 * 60, week=41).pop()
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                           for sl in ttmodel.wdb.slots_intersecting[mardi_11h]
                                           for c in set(C) & ttmodel.wdb.compatible_courses[sl]),
                               '==',
                               0,
                               constraint_type="Conf satellites")

    # if 6 in ttmodel.weeks and ttmodel.year == 2020:
    #     mardi_4 = days_filter(ttmodel.wdb.days, week=6, day=Day.TUESDAY).pop()
    #     mardi_11h_16h = set(sl for sl in slots_filter(ttmodel.wdb.slots, day=mardi_4)
    #                         if 11*60 <= sl.start_time < 15*60 + 45)
    #     # ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
    #     #                                    for slot in mardi_11h_16h
    #     #                                    for sl in ttmodel.wdb.slots_intersecting[slot]
    #     #                                    for c in ttmodel.wdb.compatible_courses[sl]),
    #     #                        '==',
    #     #                        0,
    #     #                        "Journee d'ateliers citoyens")
    #     for slot in mardi_11h_16h:
    #         ttmodel.add_to_slot_cost(slot, 100 * ttmodel.sum(ttmodel.TT[sl, c]
    #                                                          for sl in ttmodel.wdb.slots_intersecting[slot]
    #                                                          for c in ttmodel.wdb.compatible_courses[sl]))
    #     for i in ttmodel.wdb.instructors:
    #         ttmodel.add_constraint(ttmodel.IBD[(i, mardi_4)],
    #                                '==',
    #                                1)


def add_iut_blagnac_lp(ttmodel):
    lp = TrainingProgramme.objects.get(abbrev='APSIO')
    if ttmodel.wdb.courses.filter(group__train_prog=lp).exists():
        print("adding LP constraints")
        # Avoid first and last slot at the same time for train_prog 3
        R = ReasonableDays(train_prog=lp,
                           weight=max_weight)
        R.save()
        R.delete()

        # Force that only 3 courses are the same HD, and only on 2 HD if 4 courses
        M = MinHalfDays(join2courses=True, weight=max_weight)
        M.save()
        for module in ttmodel.wdb.modules.filter(train_prog=lp):
            M.modules.add(module)
        M.save()
        for week in ttmodel.weeks:
            M.enrich_model(ttmodel, week, ponderation=100)
        M.delete()

        # Alexandre Journaux (AJ, intervenant APSIO) préfère avoir 2 créneaux consécutifs.
        AJ = Tutor.objects.get(username='AJ')
        if AJ in ttmodel.wdb.instructors:
            M = MinHalfDays(join2courses=True)
            M.save()
            M.tutors.add(AJ)
            M.save()
            for week in ttmodel.weeks:
                M.enrich_model(ttmodel, week)
            M.delete()

        B219 = RoomGroup.objects.get(name='B219')
        ttmodel.add_constraint(
            ttmodel.sum(ttmodel.TTrooms[(sl, c, B219)]
                        for sl in ttmodel.wdb.slots
                        for c in set(ttmodel.wdb.courses.exclude(group__train_prog=lp))
                        & ttmodel.wdb.compatible_courses[sl]
                        if B219 in ttmodel.wdb.room_groups_for_type[c.room_type]),
            '==',
            0,
            constraint_type='B219_to_LP')


def add_iut_blagnac_info(ttmodel):
    DS = CourseType.objects.get(name='DS', department=ttmodel.department)
    CM = CourseType.objects.get(name='CM', department=ttmodel.department)
    TD = CourseType.objects.get(name='TD', department=ttmodel.department)
    print("finally, adding info specific constraints")

    # Limit Long Days for instructors
    R = ReasonableDays(weight=max_weight)
    R.save()
    for i in ttmodel.wdb.instructors:
        R.tutors.add(i)
    R.save()
    # R.enrich_model(ttmodel, ponderation=ttmodel.lim_ld)
    R.delete()

    # Impose pour certains vacataires le fait qu'ils viennent sur une seule demi-journée (si moins de 3 cours)
    # C'EST CETTE CONTRAINTE, LORSQU'ELLE N'EST QUE PREFERENCE, QUI CREE LA PAGAILLE DANS CBC!!!
    M = MinHalfDays(join2courses=True, weight=max_weight)
    M.save()
    for i in ttmodel.wdb.instructors:
        if i.username in ['AB', 'AJ', 'CDU', 'FMA', 'GRJ', 'JD', 'SD', 'FMO',
                          'JPC', 'MN', 'NJ', 'TC', 'XB', 'PDU', 'VG', 'LC', 'MTH', 'BB']:
            M.tutors.add(i)
    M.save()
    for week in ttmodel.weeks:
        M.enrich_model(ttmodel, week, ponderation=1000)
    M.delete()

    # 2019 / 2020
    # Semaine 41 et 42: IC veut venir au moins 4 jours différents
    IC = Tutor.objects.get(username='IC')
    if IC in ttmodel.wdb.instructors:
        for week in {41, 42}:
            if week in ttmodel.weeks:
                ttmodel.add_constraint(ttmodel.sum(ttmodel.IBD[IC, d] for d in
                                                   days_filter(ttmodel.wdb.days, week=week)),
                                       '>=',
                                       4,
                                       constraint_type="4 jours au moins pour IC")
        # IC : Si cours à 15h45, cours également à 17h15 (préférence)
        for d in ttmodel.wdb.days:
            sl15 = slots_filter(ttmodel.wdb.slots, day=d, start_time=15 * 60 + 45).pop()
            sl17 = slots_filter(ttmodel.wdb.slots, day=d, start_time=17 * 60 + 15).pop()
            B2 = ttmodel.add_conjunct(ttmodel.IBS[IC, sl15], ttmodel.IBS[IC, sl17])
            ttmodel.add_to_inst_cost(IC, ttmodel.IBS[IC, sl15] - B2, week=d.week)

    # if 43 in ttmodel.weeks :
    #     Exam_EE = ttmodel.wdb.courses.get(type__name='DS', module__abbrev='EE')
    #     Exam_FO = ttmodel.wdb.courses.get(type__name='DS', module__abbrev='FO')
    #     for sl in ttmodel.wdb.compatible_slots[Exam_EE]:
    #         ttmodel.add_constraint(ttmodel.TT[(sl,Exam_EE)] - ttmodel.TT[(sl, Exam_FO)], '==', 0,
    #                                'Exams de EE et FO en parallele %s' % sl)

    # si PDU vient à 8h, il ne vient pas ni à 11 ni à 14.
    PDU = Tutor.objects.get(username='PDU')
    if PDU in ttmodel.wdb.instructors:
        for day in ttmodel.wdb.days:
            sl8 = slots_filter(ttmodel.wdb.slots, day=day, start_time=8 * 60).pop()
            sl11 = slots_filter(ttmodel.wdb.slots, day=day, start_time=11 * 60).pop()
            sl14 = slots_filter(ttmodel.wdb.slots, day=day, start_time=14 * 60 + 15).pop()
            ttmodel.add_constraint(
                ttmodel.IBS[PDU, sl8] + 0.5 * (ttmodel.IBS[PDU, sl11] + ttmodel.IBS[PDU, sl14]),
                '<=',
                1,
                constraint_type="spécificites PDU", days=day)

    # MN : pas plus de 2 cours par demie-journée
    # En base?

    # Semaine 40 : WE d'intégration
    if 40 in ttmodel.weeks and ttmodel.year == 2019:
        print("WE d'intégration")
        for sl in slots_filter(ttmodel.wdb.slots, week_day=Day.FRIDAY, apm=Time.PM, week=40):
            for c in set(course for course in
                         ttmodel.wdb.compatible_courses[sl]
                         if course.group.train_prog.abbrev != 'APSIO'):
                if c.type.name == 'TD':
                    coeff = 2
                elif c.type.name == 'DS':
                    coeff = 10
                elif c.type.name == 'CM':
                    coeff = 8
                else:
                    coeff = 1
                # coeff *= 10
                if sl.start_time > 14 * 60 + 15:
                    coeff *= 2
                ttmodel.add_to_slot_cost(sl, coeff * ttmodel.TT[(sl, c)])
    # Trucs du passé...

    # Les séances de réflexion pédagogiques ont lieu à 9h, 11h ou 14h pour les 2 train_progs en même temps
    cms_peda = ttmodel.wdb.courses.filter(module__abbrev='Réfl. Péda')
    if len(cms_peda) == 2:
        c1 = cms_peda[0]
        c2 = cms_peda[1]
        for sl in ttmodel.wdb.compatible_slots[c1]:
            if sl.start_time > 15 * 60 or sl.start_time < 9 * 60:
                ttmodel.add_constraint(ttmodel.TT[(sl, c1)] +
                                       ttmodel.TT[(sl, c2)], '==', 0,
                                       constraint_type="reu_peda", slot=sl)
            else:
                ttmodel.add_constraint(ttmodel.TT[(sl, c1)] -
                                       ttmodel.TT[(sl, c2)], '==', 0,
                                       constraint_type="reu_peda", slot=sl)

    # Éviter que EPE ait un cours à 8h et un à 15h45 le même jour...)
    # prof_epe = Tutor.objects.get(username='EPE')
    # if prof_epe in ttmodel.wdb.instructors:
    #     cours_epe = ttmodel.wdb.courses.filter(tutor=prof_epe)
    #     for sl1 in ttmodel.wdb.slots.filter(heure__hours=8):
    #         for sl2 in ttmodel.wdb.slots.filter(jour=sl1.jour, heure__hours=15):
    #             for c1 in cours_epe:
    #                 for c2 in cours_epe.exclude(id__lte=c1.id):
    #                     ttmodel.add_constraint(
    #                         ttmodel.TT[(sl1, c1)] + ttmodel.TT[(sl2, c2)],
    #                         '<=',
    #                         1)

    # Si MN vient le vendredi après-midi, elle ne vient pas un autre matin
    # prof_mn = Tutor.objects.get(username='MN')
    # if prof_mn in ttmodel.wdb.instructors:
    #     v = Day.objects.get(no=4)
    #
    #     # vérifie si c'est possible dans l'idéal
    #     avail_slots_before_friday_noon = 0
    #     for sl in ttmodel.avail_instr[prof_mn]:
    #         if (sl.jour.day != Day.FRIDAY or sl.heure.apm != Time.PM) and ttmodel.avail_instr[prof_mn][sl] != 0:
    #             avail_slots_before_friday_noon += 1
    #
    #     if len(ttmodel.wdb.courses.filter(tutor=prof_mn)) \
    #             < avail_slots_before_friday_noon:
    #         for d in ttmodel.wdb.days.exclude(no=4):
    #             ttmodel.add_constraint(
    #                 ttmodel.IBHD[(prof_mn, v, Time.PM)] + ttmodel.IBHD[(prof_mn, d, Time.AM)],
    #                 '<=',
    #                 1)

    # Eviter que PSO ait un TD/TP juste avant un amphi
    # prof_pso = Tutor.objects.get(username='PSO')
    # if prof_pso in ttmodel.wdb.instructors:
    #     cm_ds_pso = ttmodel.wdb.courses.filter(tutor=prof_pso,
    #                                            type__in=[CM, DS])
    #
    #     for c in cm_ds_pso:
    #         for sl in ttmodel.wdb.slots.exclude(heure__hours=8) \
    #                 .exclude(heure__hours=14):
    #             slots_list = list(ttmodel.wdb.slots)
    #             sl_rank = slots_list.index(sl)
    #             sl_precedent = slots_list[sl_rank-1]
    #             for c2 in ttmodel.wdb.courses.filter(tutor=prof_pso) \
    #                     .exclude(id__lte=c.id):
    #                 ttmodel.add_constraint(
    #                     ttmodel.TT[(sl, c)] + ttmodel.TT[(sl_precedent, c2)],
    #                     '<=',
    #                     1)

    # Si AJ a plus de 3 creneaux, il préfère venir 2 jours differents
    prof_aj = Tutor.objects.get(username='AJ')
    if len(ttmodel.wdb.courses.filter(tutor=prof_aj)) > 3:
        ttmodel.add_constraint(ttmodel.IBD_GTE[2][prof_aj], '==', 1,
                               constraint_type="Si AJ a plus de 3 creneaux, il préfère venir 2 jours differents")

    # LN prefere ne pas avoir 2 TD de la meme matiere d'affilée avec deux groupes différents
    # prof_ln = Tutor.objects.get(username='LN')
    # if prof_ln in ttmodel.wdb.instructors:
    #     for c in ttmodel.wdb.courses.filter(tutor=prof_ln, type=TD):
    #         for c2 in ttmodel.wdb.courses.filter(tutor=prof_ln,
    #                                              module=c.module,
    #                                              type=TD) \
    #                 .exclude(group=c.group):
    #             slots_list = list(ttmodel.wdb.slots)
    #
    #             for sl in ttmodel.wdb.slots:
    #                 if sl.heure.hours < 17:
    #                     sl_rank = slots_list.index(sl)
    #                     sl_suivant = slots_list[sl_rank + 1]
    #
    #                     ttmodel.obj += ttmodel.add_conjunct(ttmodel.TT[(sl, c)], ttmodel.TT[(sl_suivant, c2)])

    # VG et AO sont toujours dans la même salle!

    for week in ttmodel.weeks:
        if week != 36:
            B008 = RoomGroup.objects.get(name='B008')
            B007 = RoomGroup.objects.get(name='B007')
            B005 = RoomGroup.objects.get(name='B005')
            Exam = RoomGroup.objects.filter(name__in=['A011', 'Exam'])[0]
            for c in ttmodel.wdb.courses.filter(tutor__username='VG', type=TD, room_type__in=B008.types.all()):
                for sl in ttmodel.wdb.compatible_slots[c]:
                    for rg in RoomGroup.objects.filter(types__in=[c.room_type]).exclude(id=B008.id):
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c, rg)], '==', 0,
                                               constraint_type="VG et AO sont toujours dans la même salle!")
            for c in ttmodel.wdb.courses.filter(tutor__username='VG').exclude(room_type__in=B008.types.all()):
                for sl in ttmodel.wdb.compatible_slots[c]:
                    for rg in RoomGroup.objects.filter(types__in=[c.room_type]).exclude(id__in=[B007.id, Exam.id]):
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c, rg)], '==', 0,
                                               constraint_type="VG et AO sont toujours dans la même salle!")
            for c in ttmodel.wdb.courses.filter(tutor__username='AO', type=TD, room_type__in=B005.types.all()):
                for sl in ttmodel.wdb.compatible_slots[c]:
                    for rg in RoomGroup.objects.filter(types__in=[c.room_type]).exclude(id=B005.id):
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c, rg)], '==', 0,
                                               constraint_type="VG et AO sont toujours dans la même salle!")

    # Semaine de réunion péda ou d'équipe
    if ttmodel.year == 2020:
        for week in [2, 5, 7, 14]:
            if week in ttmodel.wdb.weeks:
                for day in days_filter(ttmodel.wdb.days, week=week, day=Day.THURSDAY):
                    for i in set(tutor for tutor in ttmodel.wdb.instructors if tutor.status == Tutor.FULL_STAFF):
                        ttmodel.add_constraint(ttmodel.IBD[(i, day)],
                                               '==',
                                               1, constraint_type="Semaine de réunion péda ou d'équipe")

    #######################A REVOIR:
    # CDU veut venir une journée entière (et le lendemain à 8h) quand il a 6 créneaux (ou 7)
    prof_cdu = Tutor.objects.get(username='CDU')
    if prof_cdu in ttmodel.wdb.instructors:
        for week in ttmodel.weeks:
            cours_cdu = set(c for c in ttmodel.wdb.courses_for_tutor[prof_cdu] if c.week == week)
            if len(cours_cdu) >= 6:
                cdu6 = {}
                jours = [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY]
                for rang, jour in enumerate([Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY]):
                    cdu6[jour] = ttmodel.add_var("cdu6_%s" % jour)
                    slots = slots_filter(ttmodel.wdb.slots, week_day=jour, week=week)
                    jour_sum = ttmodel.sum(
                        ttmodel.TT[sl, c] for sl in slots for c in cours_cdu & ttmodel.wdb.compatible_courses[sl])
                    ttmodel.add_constraint(jour_sum - cdu6[jour], '<=', 5,
                                           constraint_type="CDU veut venir une journée entière quand il a 6 créneaux")  # vaut 1 si day_sum = 6
                    ttmodel.add_constraint(jour_sum - 6 * cdu6[jour], '>=', 0,
                                           constraint_type="CDU veut venir une journée entière quand il a 6 créneaux")  # vaut 0 si day_sum < 6
                    if len(cours_cdu) == 7:
                        suivant_8h = slots_filter(ttmodel.wdb.slots, week_day=jours[rang + 1], start_time=8 * 60,
                                                  week=week).pop()
                        ttmodel.add_constraint(
                            cdu6[jour] -
                            ttmodel.sum(ttmodel.TT[suivant_8h, c] for c in
                                        cours_cdu & ttmodel.wdb.compatible_courses[suivant_8h]),
                            '==',
                            0, constraint_type="CDU veut venir une journée entière quand il a 7 créneaux")
                ttmodel.add_constraint(ttmodel.sum(cdu6[jour] for jour in cdu6), '==', 1,
                                       constraint_type="CDU veut venir une journée entière quand il a 7 créneaux")

    # Semaine 49, nuit de l'info
    if 49 in ttmodel.weeks and ttmodel.year == 2018:
        for sl in slots_filter(ttmodel.wdb.slots, week_day=Day.THURSDAY, week=49):
            for c in ttmodel.wdb.compatible_courses[sl]:
                if (c.group.train_prog.abbrev == 'INFO2' and c.group.name in {'2B'}) \
                        or (c.group.train_prog.abbrev == 'INFO1' and c.group.name in {'4A'}):
                    ttmodel.obj += ttmodel.TT[(sl, c)]
                ttmodel.obj += ttmodel.TT[(sl, c)]

    # Semaine 3 exam d'ISI
    if 3 in ttmodel.weeks and ttmodel.year == 2020:
        C = set(ttmodel.wdb.courses.filter(module__abbrev='ISI', type__name='TP'))
        used_slot = {}
        for sl in slots_filter(ttmodel.wdb.slots, week=3):
            used_slot[sl] = ttmodel.add_var("ISI_%s" % sl)
            ttmodel.add_constraint(10 * used_slot[sl] -
                                   ttmodel.sum(ttmodel.TT[sl, c] for c in C & ttmodel.wdb.compatible_courses[sl]),
                                   '>=', 0, constraint_type="Semaine 3 exam d'ISI")
        ttmodel.add_constraint(ttmodel.sum(used_slot[sl] for sl in ttmodel.wdb.slots), '<=', 2,
                               constraint_type="Semaine 3 exam d'ISI")

    if 5 in ttmodel.weeks and ttmodel.year == 2020:
        C1 = ttmodel.wdb.courses.filter(type__name='CM', module__abbrev='PR', group__name='1')
        C4 = ttmodel.wdb.courses.filter(type__name='TD', module__abbrev='PR', group__name='4')
        for i in range(2):
            c1 = C1[i]
            c4 = C4[i]
            for sl in ttmodel.wdb.compatible_slots[c1]:
                ttmodel.add_constraint(ttmodel.TT[sl, c1] -
                                       ttmodel.sum(ttmodel.TT[sl1, c4] for sl1 in
                                                   slots_filter(ttmodel.wdb.compatible_slots[c4], simultaneous_to=sl)),
                                       '==',
                                       0, constraint_type="Semaine 5 module PR groupe 1 et 4")

    # Semaine 4 PTUT le jeudi et le vendredi

    if 4 in ttmodel.weeks and ttmodel.year == 2019:
        C = ttmodel.wdb.courses.filter(group__train_prog__abbrev='INFO2')
        for day in [Day.THURSDAY, Day.FRIDAY]:
            ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                               for c in C
                                               for sl in slots_filter(ttmodel.wdb.slots, week_day=day, week=4)
                                               & ttmodel.wdb.compatible_slots[c])
                                   , '==',
                                   0,
                                   constraint_type="PTUT_no_Courses", days=day)

    # Paul et Pablo ont un créneau de libre le lundi à 11h, sauf s'ils n'ont aucun jours en commun...
    # Paul = Tutor.objects.get(username='PRG')
    # Pablo = Tutor.objects.get(username='PSE')
    # if False and Paul in ttmodel.wdb.instructors and Pablo in ttmodel.wdb.instructors:
    #     commun = {}
    #     Les_deux_pas_cours_a_11h = {}
    #     for d in ttmodel.wdb.days:
    #         sl_11h=ttmodel.wdb.slots.get(jour=d, heure__hours=11)
    #         Pablo_11h = ttmodel.add_or([ttmodel.TT[sl_11h,c] for c in ttmodel.wdb.courses_for_tutor[Pablo]])
    #         Paul_11h = ttmodel.add_or([ttmodel.TT[sl_11h,c] for c in ttmodel.wdb.courses_for_tutor[Paul]])
    #         commun[d] = ttmodel.add_conjunct(ttmodel.IBD[(Paul, d)],ttmodel.IBD[(Pablo, d)])
    #         Les_deux_pas_cours_a_11h[d] = ttmodel.add_conjunct(ttmodel.add_neg(Pablo_11h), ttmodel.add_neg(Paul_11h))
    #     pas_de_commun = ttmodel.add_neg(ttmodel.add_or([commun[d] for d in ttmodel.wdb.days]))
    #     ttmodel.add_constraint(pas_de_commun +
    #                            ttmodel.sum([ttmodel.add_conjunct(commun[d], Les_deux_pas_cours_a_11h[d]) for d in ttmodel.wdb.days])
    #                            , '>=',
    #                            1)

    # Semaine 6, Jury le vendredi!
    if 6 in ttmodel.weeks and ttmodel.year == 2019:
        vendredi = ttmodel.wdb.days.get(day=Day.FRIDAY)
        for i in ttmodel.wdb.instructors:
            if i.status == Tutor.FULL_STAFF:
                ttmodel.add_constraint(ttmodel.IBD[(i, vendredi)],
                                       '==',
                                       1, constraint_type="Semaine 6, Jury le vendredi")
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[(sl, c)]
                                           for i in ttmodel.wdb.instructors if i.status == Tutor.FULL_STAFF
                                           for c in ttmodel.wdb.courses_for_tutor[i]
                                           for sl in slots_filter(ttmodel.wdb.slots, week_day=Day.FRIDAY, apm=Time.PM,
                                                                  week=6)
                                           & ttmodel.wdb.compatible_slots[c]),
                               '==',
                               0,
                               constraint_type='Jury')
    # Semaine FLOP
    if 9 in ttmodel.weeks and ttmodel.year == 2020:
        for c in ttmodel.wdb.courses.filter(module__abbrev='FLOP'):
            sc = ScheduledCourse.objects.get(course=c, work_copy=14)
            slots = slots_filter(ttmodel.wdb.slots, week_day=sc.day, start_time=sc.start_time)
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.TTrooms[(slot, c, sc.room)] for slot in slots & ttmodel.wdb.compatible_slots[c]),
                '==',
                1, constraint_type="Semaine FLOP")

    # SF veut venir une matinée entière et un autre jour à 8h
    # SF = Tutor.objects.get(username='SF')
    # if SF in ttmodel.wdb.instructors:
    #     cours_sf=ttmodel.wdb.courses_for_tutor[SF]
    #     if cours_sf.count() >= 4:
    #         sf3={}
    #         for jour in ttmodel.wdb.days:
    #             sf3[jour] = ttmodel.add_var("sf3_%s"%jour)
    #             slots = ttmodel.wdb.slots.filter(jour=jour, heure__apm=Time.AM)
    #             jour_sum = ttmodel.sum(
    #                 ttmodel.TT[sl, c] for sl in slots for c in cours_sf)
    #             ttmodel.add_constraint(jour_sum - sf3[jour], '<=', 2)  # vaut 1 si jour_sum = 3
    #             ttmodel.add_constraint(jour_sum - 3 * sf3[jour], '>=', 0)  # vaut 0 si jour_sum < 3
    #
    #         slots_8h = ttmodel.wdb.slots.filter(heure__hours=8)
    #         ttmodel.add_constraint(
    #             ttmodel.sum(sf3[jour] for jour in ttmodel.wdb.days),
    #             '==',
    #             1,
    #             name="SF_half_day")
    #         ttmodel.add_constraint(
    #             ttmodel.sum(ttmodel.TT[sl_8h, c] for c in cours_sf for sl_8h in slots_8h),
    #             '>=',
    #             2,
    #             name="SF_8h")

    #  LN veut minimiser les demi_journées en LP

    if ttmodel.wdb.modules.filter(abbrev="Scrum").exists():
        scrum = ttmodel.wdb.modules.get(abbrev='Scrum')
        M = MinHalfDays(join2courses=True)
        M.save()
        M.modules.add(scrum)
        M.save()
        for week in ttmodel.weeks:
            M.enrich_model(ttmodel, week)
        M.delete()

    # Trucs du passé:
    #
    # # Semaine 23, un peu spéciale... Le PTUT a lieu du lundi au mercredi, le reste ensuite
    # if 23 in ttmodel.weeks:
    #     for c in ttmodel.wdb.courses.filter(group__train_prog=1,
    #                                         module__abbrev='PTUT'):
    #         sl = ttmodel.wdb.slots.get(id=1)
    #         if c.type == Cours.TD:
    #             ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 1)
    #         else:
    #             ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #             for sl in ttmodel.wdb.slots.filter(jour__no__gte=3):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #     for c in ttmodel.wdb.courses.filter(group__train_prog=1) \
    #             .exclude(module__abbrev='PTUT'):
    #         for sl in ttmodel.wdb.slots.filter(jour__no__lte=2):
    #             ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #
    # # Semaine 20 bizarre

    # if 20 in ttmodel.weeks:
    #     for c in ttmodel.wdb.courses.filter(group__train_prog=1):
    #         if c.room_type.name == 'A':
    #             for sl in ttmodel.wdb.slots.exclude(heure__no=0, jour__no__lte=3):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #         if c.room_type.name == '6M':
    #             for sl in ttmodel.wdb.slots.filter(heure__no__gte=3).exclude(jour__no=4):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #         for sl in ttmodel.wdb.slots.filter(heure__no=5):
    #             ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #
    # # Semaine 6, Jury!
    # if 6 in ttmodel.weeks and ttmodel.year == 2018:
    #     for i in ttmodel.wdb.instructors.filter(statut=Tutor.FULL_STAFF):
    #         ttmodel.add_constraint(ttmodel.IBD[(i, Jour.objects.get(no=4))],
    #                                '==',
    #                                1)
    #         for c in ttmodel.wdb.courses.filter(tutor=i):
    #             for sl in ttmodel.wdb.slots.filter(jour__no=4,
    #                                                heure__no__gte=3,
    #                                                heure__no__lte=4):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)

    # # Pas d'examen le vendredi 6 avril, semaine 14:
    # if (ttmodel.week, ttmodel.year) == (14, 2018):
    #     for c in ttmodel.wdb.courses.filter(type='DS'):
    #         for sl in ttmodel.wdb.slots.filter(jour__no=4):
    #             ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #
    # # Les TP de OM seront simultanés en semaine 25
    # prof_om = Tutor.objects.get(username='OM')
    # if 25 in ttmodel.weeks 25:
    #     tp1A = ttmodel.wdb.courses.get(tutor=prof_om, group__name='1A1A')
    #     tp1B = ttmodel.wdb.courses.get(tutor=prof_om, group__name='1A1B')
    #     tp2A = ttmodel.wdb.courses.get(tutor=prof_om, group__name='1A2A')
    #     tp2B = ttmodel.wdb.courses.get(tutor=prof_om, group__name='1A2B')
    #     SimultaneousCourses(course1=tp1A, course2=tp1B).enrich_model(ttmodel)
    #     SimultaneousCourses(course1=tp2A, course2=tp2B).enrich_model(ttmodel)
    #
    #     # Semaine 36
    #     if 36 in ttmodel.weeks 36:
    #         # Pas de TP S3 le lundi PM
    #         for sl in Creneau.objects.filter(jour=0, heure__apm='PM'):
    #             for c in ttmodel.wdb.courses.filter(group__promo=2, nature='TP'):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #         # Pas de cours le lundi AM
    #         for sl in Creneau.objects.filter(jour=0, heure__apm='AM'):
    #             for c in ttmodel.wdb.courses.filter(group__promo=2):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #
    #         # Pas de cours planifiés S1 le lundi et le mardi
    #         for sl in Creneau.objects.filter(jour__in=[0, 1]):
    #             for c in ttmodel.wdb.courses.filter(group__promo=1):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #
    #     # Semaine 42, conf à 11h le lundi
    #     if 42 in ttmodel.weeks:
    #         for sl in Creneau.objects.filter(jour=0, heure__no=2):
    #             for c in ttmodel.wdb.courses.filter(group__promo__in=[2, 3]).exclude(module__abbrev='Conf'):
    #                 ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #
    #     # Semaines 41 à 45 : Les TP de ZU ont lieu pendant un TP de IO
    #     if ttmodel.week in range(41, 46):
    #         TPs_IO = ttmodel.wdb.courses.filter(module__abbrev='PSE',
    #                                             nature='TP',
    #                                             prof__user__username='IO')
    #
    #         TPs_ZU = ttmodel.wdb.courses.filter(module__abbrev='PSE',
    #                                             nature='TP',
    #                                             prof__user__username='ZU')
    #         for sl in ttmodel.wdb.slots:
    #             IO_SUM = ttmodel.sum(ttmodel.TT[(sl, c)] for c in TPs_IO)
    #             ZU_SUM = ttmodel.sum(ttmodel.TT[(sl, c)] for c in TPs_ZU)
    #             ttmodel.add_constraint(IO_SUM - ZU_SUM, '>=', 0)
    #     # Le groupe 2A3 n'a pas cours le lundi à 17h
    #     lu17h = ttmodel.wdb.slots.get(jour__no=0, heure__no=5)
    #     for c in ttmodel.wdb.courses.filter(group__name__in=['2A3', '2A3A', '2A3B']):
    #         ttmodel.add_constraint(ttmodel.TT[(lu17h, c)], '==', 0)
    #
    #     # Réunion flop le 19/11
    #     if ttmodel.week in [47] and ttmodel.year == 2018:
    #         for i in ttmodel.wdb.instructors.filter(user__username__in=['PSE', 'PRG', 'IO']):
    #             ttmodel.add_constraint(ttmodel.IBD[(i, Jour.objects.get(no=3))],
    #                                    '==',
    #                                    1)
    # #Semaine 45, PTUT "entretien d'embauche" le jeudi matin
    # if 45 in ttmodel.weeks  and ttmodel.year==2018:
    #     for sl in Creneau.objects.exclude(jour=3):
    #         for c in ttmodel.wdb.courses.filter(prof__user__username='---', module__abbrev='PTUT'):
    #             ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)
    #


def add_iut_blagnac_rt(ttmodel):
    print("finally, adding RT specific constraints")
    RT = Department.objects.get(abbrev='RT')
    local_var_un = ttmodel.add_var("UN")
    ttmodel.add_constraint(local_var_un, '==', 1)

    # Les tp d'expression-Com. et d'anglais de 2h doivent être en quinconce
    # dans la mesure où y'en a le même nombre...
    M = Module.objects.filter(train_prog__department=RT)
    for i in range(1, 5):
        # J'annule!
        continue
        A = M.get(abbrev='ANG' + str(i))
        EC = M.get(abbrev='EC' + str(i))
        C_A = ttmodel.wdb.courses.filter(type__name='TP120', module=A)
        C_EC = ttmodel.wdb.courses.filter(type__name='TP120', module=EC)
        a = C_A.count()
        ec = C_EC.count()
        if a > 0:
            if a == ec:
                relation = '=='
            elif a < ec:
                relation = '<='
            else:
                relation = '>='
            contrainte = True
            for sl in ttmodel.wdb.compatible_slots[C_A[0]]:
                if contrainte:
                    ttmodel.add_constraint(
                        ttmodel.sum(ttmodel.TT[sl, c] for c in C_A) - ttmodel.sum(ttmodel.TT[sl, c] for c in C_EC),
                        relation,
                        0)
                else:
                    if a < ec:
                        ttmodel.add_to_slot_cost(sl, ttmodel.sum(ttmodel.TT[sl, c] for c in C_EC) - ttmodel.sum(
                            ttmodel.TT[sl, c] for c in C_A))
                    else:
                        ttmodel.add_to_slot_cost(sl,
                                                 ttmodel.sum(ttmodel.TT[sl, c] for c in C_A) - ttmodel.sum(
                                                     ttmodel.TT[sl, c] for c in C_EC))

    # CONTRAINTE : Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière
    # PREFERENCE FORTE : LES TP240 sont en parallèle (dont au moins un permanent)
    ct = ttmodel.wdb.course_types.get(name='TP240')
    for week in ttmodel.weeks:
        for m in ttmodel.wdb.modules.filter(period__department=RT):
            assez_de_permanents = True
            courses = ttmodel.wdb.courses.filter(module=m, type=ct, week=week)
            if courses.filter(tutor__status='fs').count() < courses.filter(tutor__status='ss').count():
                assez_de_permanents = False
            courses = set(courses)
            tp240unique = {}
            for sl in slots_filter(ttmodel.wdb.slots, course_type=ct, week=week):
                moins_de_2 = ttmodel.add_var('moins_de_deux%s_%s' % (m, sl))
                au_moins_1 = ttmodel.add_var('au_moins_1%s_%s' % (m, sl))
                ttmodel.add_constraint(au_moins_1 -
                                       ttmodel.sum(ttmodel.TT[sl, c]
                                                   for c in courses & ttmodel.wdb.compatible_courses[sl]),
                                       '<=',
                                       0,
                                       constraint_type="Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière")
                ttmodel.add_constraint(10 * au_moins_1 -
                                       ttmodel.sum(ttmodel.TT[sl, c]
                                                   for c in courses & ttmodel.wdb.compatible_courses[sl]),
                                       '>=',
                                       0,
                                       constraint_type="Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière")
                ttmodel.add_constraint(2 * moins_de_2 +
                                       ttmodel.sum(ttmodel.TT[sl, c]
                                                   for c in courses & ttmodel.wdb.compatible_courses[sl]),
                                       '>=',
                                       2,
                                       constraint_type="Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière")
                ttmodel.add_constraint(2 * moins_de_2 +
                                       ttmodel.sum(ttmodel.TT[sl, c]
                                                   for c in courses & ttmodel.wdb.compatible_courses[sl]),
                                       '<=',
                                       4,
                                       constraint_type="Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière")
                tp240unique[sl] = ttmodel.add_conjunct(moins_de_2, au_moins_1)
                ttmodel.add_to_slot_cost(sl, 100 * tp240unique[sl])
            if not assez_de_permanents:
                continue
            for sl in slots_filter(ttmodel.wdb.slots, course_type=ct, week=week):
                vacataires = ttmodel.sum(ttmodel.TT[sl, c]
                                         for c in courses & ttmodel.wdb.compatible_courses[sl]
                                         if c.tutor.status == 'ss')
                permanents = ttmodel.sum(ttmodel.TT[sl, c]
                                         for c in courses & ttmodel.wdb.compatible_courses[sl]
                                         if c.tutor.status == 'fs')
                vacataires_sans_permanents = ttmodel.add_var("vacataires_sans_permanents_%s_%s" % (m, sl))
                ttmodel.add_constraint(10 * vacataires_sans_permanents + permanents - vacataires, '<=', 10,
                                       constraint_type="vacataires_sans_permanents", slot=sl, module=m)

                ttmodel.add_constraint(vacataires - permanents - 10 * vacataires_sans_permanents,
                                       '<=',
                                       0,
                                       constraint_type="vacataires_sans_permanents", slot=sl, module=m)
                ttmodel.add_to_slot_cost(sl, 100*vacataires_sans_permanents)

    # Quand même par paire, et chaque vacataire doit avoir un permanent...

    # Eviter les trous pour les étudiants
    # --> A priori c'est ok avec les préférences des types de cours

    # Pas plus de 1 TD d'une matière par demie-journée pour chaque groupe sauf pour ENT1
    for m in ttmodel.wdb.modules.filter(period__department=RT).exclude(abbrev='ENT1'):
        for g in ttmodel.wdb.groups.filter(type__name='TD'):
            for d in ttmodel.wdb.days:
                for apm in [Time.AM, Time.PM]:
                    ttmodel.add_constraint(
                        ttmodel.sum(ttmodel.TT[sl, c]
                                    for c in ttmodel.wdb.courses.filter(module=m, group=g, type__name='TD')
                                    for sl in slots_filter(ttmodel.wdb.slots, day=d, apm=apm)
                                    & ttmodel.wdb.compatible_slots[c]),
                        '<=',
                        2,
                        constraint_type="Pas plus d'un TD par demie-journee", module=m, group=g, days=d, apm=apm
                    )

    # minimiser les demie-journées pour tous les vacataires + regrouper les cours si 2 par demie-journée
    contrainte = False
    for t in ttmodel.wdb.instructors:
        if t.status == 'ss':
            for week in ttmodel.weeks:
                heures = sum(c.type.duration for c in ttmodel.wdb.courses_for_tutor[t] if c.week == week) / 60
                nb_dj_min = heures / 4.5
                if nb_dj_min != int(nb_dj_min):
                    nb_dj_min = int(nb_dj_min) + 1
                total_dj = ttmodel.sum(ttmodel.IBHD[(t, d, apm)]
                                       for d in days_filter(ttmodel.wdb.days, week=week)
                                       for apm in [Time.AM, Time.PM])
                if contrainte:
                    ttmodel.add_constraint(total_dj,
                                           '<=',
                                           nb_dj_min,
                                           constraint_type="Min_Half_Days", instructor=t)
                else:
                    ttmodel.add_to_inst_cost(t, 1000 * (total_dj - nb_dj_min * local_var_un), week=week)

    # 4h max par demie journée pour PCOU, LAND
    for t in ttmodel.wdb.instructors:
        if t.username in ['PCOU', 'LAND']:
            for week in ttmodel.weeks:
                heures = sum(c.type.duration for c in ttmodel.wdb.courses_for_tutor[t] if c.week == week) / 60
                dispos = set(a for a in ttmodel.wdb.availabilities[t][week] if a.value >= 1)
                heures_dispos = sum(up.duration for up in dispos) / 60
                if heures_dispos < 1.5 * heures:
                    continue
                for d in days_filter(ttmodel.wdb.days, week=week):
                    for apm in [Time.AM, Time.PM]:
                        ttmodel.add_constraint(
                            ttmodel.sum(ttmodel.TT[sl, c] * c.type.duration
                                        for sl in slots_filter(ttmodel.wdb.slots, day=d, apm=apm)
                                        for c in ttmodel.wdb.courses_for_tutor[t]
                                        & ttmodel.wdb.compatible_courses[sl]),
                            '<=',
                            4*60, constraint_type="Pas plus de 4 heures par demie_journee",
                            instructor=t, days=d, apm=apm)

    # Pas plus de 2 examens par jour!
    DS = CourseType.objects.get(name='Examen', department=ttmodel.department)
    pas_plus_de_1_exam_par_demie_journee = True
    if pas_plus_de_1_exam_par_demie_journee:
        for promo in ttmodel.train_prog:
            L = LimitCourseTypeTimePerPeriod(max_hours=2,
                                             course_type=DS,
                                             period=LimitCourseTypeTimePerPeriod.HALF_DAY,
                                             train_prog=promo)
            L.save()
            for week in ttmodel.weeks:
                L.enrich_model(ttmodel, week)
            L.delete()

    if 36 in ttmodel.weeks:
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                           for sl in slots_filter(ttmodel.wdb.slots, start_time=8 * 60,
                                                                  week=36, week_day=Day.MONDAY)
                                           for c in set(ttmodel.wdb.courses
                                                        .filter(group__train_prog__abbrev__in=['RT2', 'RT2A'])
                                                        .exclude(module__abbrev='SC'))
                                           & ttmodel.wdb.compatible_courses[sl]),
                               '==',
                               0, constraint_type="pas de cours lundi 8h pour RT2")


def add_iut_blagnac_gim(ttmodel):
    GIM = Department.objects.get(abbrev='GIM')
    print("Finally, adding GIM' specific constraints")
    for bg in ttmodel.wdb.basic_groups.filter(train_prog__abbrev='GIM1').exclude(name__in=['1AA', '1AM']):
        for sl1 in ttmodel.wdb.slots:
            for sl2 in ttmodel.wdb.slots_intersecting[sl1] - {sl1}:
                name = 'simul_slots_1AA_1AM_' + str(bg) + '_' + str(sl1) + '_' + str(sl2)
                ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[(sl1, c1)]
                                                   for g1 in ttmodel.wdb.groups.filter(name__in=['1AA', '1AM'])
                                                   for c1 in ttmodel.wdb.courses_for_group[g1]
                                                   & ttmodel.wdb.compatible_courses[sl1]) * 0.5 +
                                       ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                                   for c2 in ttmodel.wdb.courses_for_basic_group[bg]
                                                   & ttmodel.wdb.compatible_courses[sl2]),
                                       '<=', 1, constraint_type="simul slot", group=bg, slot=[sl1, sl2])

    TPB1 = ttmodel.wdb.groups.filter(name='TPB1', train_prog__abbrev='GIM2')
    TPB2 = ttmodel.wdb.groups.filter(name='TPB2', train_prog__abbrev='GIM2')
    for m in ttmodel.wdb.modules:
        G1 = TPB1
        G2 = TPB2
        if m.abbrev in ['OMM4-STA4', 'MTS4-STA3']:
            G1 = [ttmodel.wdb.groups.get(name='TPA2', train_prog__abbrev='GIM2'),
                  ttmodel.wdb.groups.get(name='TPB2', train_prog__abbrev='GIM2')]
            G2 = [ttmodel.wdb.groups.get(name='TPB1', train_prog__abbrev='GIM2'),
                  ttmodel.wdb.groups.get(name='TPC1', train_prog__abbrev='GIM2')]
        for nb in range(len(G1)):
            C1 = list(c for c in ttmodel.wdb.courses_for_group[G1[nb]] if c.module == m)
            if C1:
                C2 = list(c for c in ttmodel.wdb.courses_for_group[G2[nb]] if c.module == m)
                if len(C1) != len(C2):
                    print("G1 et G2 n'ont pas le meme nombre de cours %s !" % m)
                    continue
                for i in range(len(C1)):
                    c1 = C1[i]
                    c2 = C2[i]
                    for sl in ttmodel.wdb.compatible_slots[c1]:
                        ttmodel.add_constraint(ttmodel.TT[sl, c1] - ttmodel.TT[sl, c2], '==', 0,
                                               constraint_type="Simul_fake", groups=[G1[nb], G2[nb]], module=m, slot=sl)

    # TPB = ttmodel.wdb.groups.get(name='TPB', train_prog__abbrev='GIM2')
    # # TPCm = ttmodel.wdb.groups.get(name='TPCm', train_prog__abbrev='GIM2')
    # # TPC = ttmodel.wdb.groups.get(name='TPC', train_prog__abbrev='GIM2')
    # # TPDm = ttmodel.wdb.groups.get(name='TPDm', train_prog__abbrev='GIM2')
    # TD2 = ttmodel.wdb.groups.get(name='TD2', train_prog__abbrev='GIM2')
    # for g1,g2 in [(TPB, TD2)]: #(TPC, TPDm), (TPB, TPCm), (TPB, TD2)]:
    #     for sl1 in ttmodel.wdb.slots:
    #         for sl2 in ttmodel.wdb.slots_intersecting[sl1] - {sl1}:
    #             name = 'simul_slots_%s_%s_%s_%s_%g' % (g1, g2, sl1, sl2, ttmodel.constraint_nb)
    #             ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[(sl1, c1)]
    #                                                for c1 in ttmodel.wdb.courses_for_group[g1]
    #                                                & ttmodel.wdb.compatible_courses[sl1]) +
    #                                    ttmodel.sum(ttmodel.TT[(sl2, c2)]
    #                                                for c2 in ttmodel.wdb.courses_for_group[g2]
    #                                                & ttmodel.wdb.compatible_courses[sl2]),
    #                                    '<=', 1, name=name)

    # Pas de cours le lundi 8h pour GIM 2

    if 36 in ttmodel.weeks:
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                           for sl in slots_filter(ttmodel.wdb.slots, start_time=8 * 60,
                                                                  week_day=Day.MONDAY, week=36)
                                           for c in set(ttmodel.wdb.courses
                                                        .filter(group__train_prog__abbrev__in=['GIM2']))
                                           & ttmodel.wdb.compatible_courses[sl]),
                               '==',
                               0, constraint_type="pas de cours lundi 8h pour GIM2")

    # Pas plus de 2 cours par jour du même module
    for m in ttmodel.wdb.modules.filter(period__department=GIM).exclude(abbrev__in=['OMM4-STA4', 'MTS4-STA3']):
        for bg in ttmodel.wdb.basic_groups:
            for d in ttmodel.wdb.days:
                ttmodel.add_constraint(
                    ttmodel.sum(ttmodel.TT[sl, c]
                                for c in ttmodel.wdb.courses_for_basic_group[bg] if c.module == m
                                for sl in slots_filter(ttmodel.wdb.slots, day=d)
                                & ttmodel.wdb.compatible_slots[c]),
                    '<=',
                    2, constraint_type="Pas plus de seance du meme module par jour", module=m, group=bg, days=d)


    # semaine 2 Les cours de NBE de PPP3 sont le vendredi
    if 2 in ttmodel.weeks:
        C = ttmodel.wdb.courses.filter(tutor__username='NBE', module__abbrev='PPP3')
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] for c in C
                                           for sl in ttmodel.wdb.compatible_slots[c] if sl.day.day != Day.FRIDAY),
                               '==',
                               0, constraint_type="semaine 2 Les cours de NBE de PPP3 sont le vendredi")
    if 6 in ttmodel.weeks:
        CDBE = ttmodel.wdb.courses.filter(tutor__username='DBE', module__abbrev='PPP2')
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] for c in CDBE
                                           for sl in ttmodel.wdb.compatible_slots[c] if
                                           sl.day.day != Day.MONDAY
                                           or sl.apm != Time.PM),
                               '==',
                               0, constraint_type="semaine 6 Les cours de DBE et PPP2 sont le lundi matin")
        CPR = ttmodel.wdb.courses.filter(tutor__username='CPR', module__abbrev='PPP2')
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] for c in CPR
                                           for sl in ttmodel.wdb.compatible_slots[c] if
                                           sl.day.day != Day.MONDAY
                                           or sl.apm != Time.PM
                                           ),
                               '==',
                               0)
        CMPH = ttmodel.wdb.courses.filter(tutor__username='MPH', module__abbrev='PPP2')
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] for c in CMPH
                                           for sl in ttmodel.wdb.compatible_slots[c] if
                                           sl.day.day != Day.THURSDAY
                                           or sl.apm != Time.AM
                                           ),
                               '==',
                               0)
        CEPI = ttmodel.wdb.courses.filter(tutor__username='EPI', module__abbrev='PPP2')
        ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] for c in CEPI
                                           for sl in ttmodel.wdb.compatible_slots[c] if
                                           sl.day.day != Day.TUESDAY
                                           or sl.apm != Time.PM
                                           ),
                               '==',
                               0)


def add_iut_blagnac_cs(ttmodel):
    CS = Department.objects.get(abbrev='CS')
    print("Finally, adding CS' specific constraints")
    # - libérer au moins un après-midi (qui peut être le vendredi) à 15h40 (+)

    # TECH : NVIG et FV le mardi aprem
    for week in ttmodel.weeks:
        FV = ttmodel.wdb.courses.filter(module__abbrev='TECH', tutor__username='FV', week=week)
        NVIG = ttmodel.wdb.courses.filter(module__abbrev='TECH', tutor__username='NVIG', week=week)
        if FV.count() == 2 or NVIG.count() == 2:
            ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c] for c in FV | NVIG
                                               for sl in ttmodel.wdb.compatible_slots[c]
                                               - slots_filter(ttmodel.wdb.compatible_slots[c],
                                                              week_day=Day.TUESDAY, apm=Time.PM, week=week)),
                                   '==',
                                   0,
                                   constraint_type="Tech le mardi aprem")

    # TECH : G1 avec NVIG et en parallèle G2 avec FV et on inverse le créneau d'après.
    # for week in range(1,51):
    #     FV = Course.objects.filter(module__abbrev='TECH', week=week, tutor__username='FV')
    #     NVIG = Course.objects.filter(module__abbrev='TECH', week=week, tutor__username='NVIG')
    #     if FV.count()!=2 or NVIG.count()!=2:
    #         continue
    #     else:
    #         FV = list(FV)
    #         NVIG = list(NVIG)
    #         d1=Dependency(cours1=FV[0], cours2=FV[1], successifs=True)
    #         d2=Dependency(cours1=FV[0], cours2=NVIG[0], successifs=True)
    #         d3=Dependency(cours1=NVIG[1], cours2=NVIG[0], successifs=True)
    #         d1.save()
    #         d2.save()
    #         d3.save()

    #  pour le module DROIT 3 du S3, je voulais mettre Exam et CC à la suite sur une demi journée
    # for week in range(1,51):
    #         Cs=list(Course.objects.filter(module__abbrev='DROIT3',week=week, type__name__in=['Exam','CC']))
    #         if not Cs:
    #             continue
    #         d1=Dependency(cours1=Cs[0], cours2=Cs[1], successifs=True)
    #         d2=Dependency(cours1=Cs[1], cours2=Cs[2], successifs=True)
    #         d1.save()
    #         d2.save()

    # Pas plus de 5 créneaux par jour pour les étudiant⋅e⋅s
    # (Pour les profs, c'est dans leur pref_...)
    for bg in ttmodel.wdb.basic_groups.filter(train_prog__department=CS):
        for day in ttmodel.wdb.days:
            ttmodel.add_constraint(
                ttmodel.sum(ttmodel.TT[sl, c]
                            for c in ttmodel.wdb.courses_for_basic_group[bg]
                            for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=day)),
                '<=',
                5,
                constraint_type="Pas plus de 5 creneau", days=day, group=bg)

    # si 3h d'intervention dans la semaine et dispo sur 2 demi-journées, concentrer sur 1 seule demi-journée (++)
    for week in ttmodel.weeks:
        M = MinHalfDays(join2courses=True, weight=max_weight)
        M.save()
        for i in ttmodel.wdb.instructors:
            if sum(c.type.duration / 60 for c in ttmodel.wdb.courses_for_tutor[i] if c.week == week) <= 180:
                M.tutors.add(i)
        M.save()

        M.enrich_model(ttmodel, week, ponderation=1000)
        M.delete()

    # - libérer le vendredi à 17h (++) --> Mis en indispo des train prog

    # - TD d'un même module la même demi-journée ou dans la journée = G1 et G2 auront TD le même jour  (++)
    for m in ttmodel.wdb.modules.filter(period__department=CS):
        g1 = ttmodel.wdb.groups.get(train_prog=m.train_prog, name__in=['1G1', '2G1'])
        g2 = ttmodel.wdb.groups.get(train_prog=m.train_prog, name__in=['1G2', '2G2'])
        Cg1 = ttmodel.wdb.courses_for_group[g1]
        Cg2 = ttmodel.wdb.courses_for_group[g2]
        if len(Cg1) == len(Cg2):
            for d in ttmodel.wdb.days:
                ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[sl, c]
                                                   for sl in ttmodel.wdb.slots_by_day[d]
                                                   for c in Cg1 & ttmodel.wdb.compatible_courses[sl])
                                       -
                                       ttmodel.sum(ttmodel.TT[sl, c]
                                                   for sl in ttmodel.wdb.slots_by_day[d]
                                                   for c in Cg2 & ttmodel.wdb.compatible_courses[sl]),
                                       '==',
                                       0,
                                       constraint_type="G1 et G2 ont cours le meme jour", module=m, days=d)
