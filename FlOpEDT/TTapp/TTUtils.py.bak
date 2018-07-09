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

from base.models import Slot, ScheduledCourse, RoomPreference
from django.db.models import Max


def basic_reassign_rooms(semaine, an, target_work_copy):
    """
    Reassign the rooms...
    """
    print "reassigning rooms to minimize moves...",

    slots = Slot.objects.all().order_by('jour', 'heure')
    for sl in slots:
        rank = list(slots.filter(jour=sl.jour, heure__apm=sl.heure.apm)).index(sl)
        if rank == 0:
            continue
        slots_list = list(slots)
        precedent_sl = slots_list[slots_list.index(sl) - 1]
        nsl = ScheduledCourse.objects.filter(cours__semaine=semaine,
                                             cours__an=an,
                                             creneau=sl,
                                             copie_travail=target_work_copy)
        # print sl
        for CP in nsl:
            precedent = ScheduledCourse \
                .objects \
                .filter(cours__semaine=semaine,
                        cours__an=an,
                        creneau=precedent_sl,
                        cours__room_type=CP.cours.room_type,
                        cours__groupe=CP.cours.groupe,
                        copie_travail=target_work_copy)
            if len(precedent) == 0:
                precedent = ScheduledCourse \
                    .objects \
                    .filter(cours__semaine=semaine,
                            cours__an=an,
                            creneau=precedent_sl,
                            cours__room_type=CP.cours.room_type,
                            cours__tutor=CP.cours.tutor,
                            copie_travail=target_work_copy)
                if len(precedent) == 0:
                    continue
            precedent = precedent[0]
            # print "### has prec, trying to reassign:", precedent, "\n\t",
            cp_using_prec = ScheduledCourse \
                .objects \
                .filter(cours__semaine=semaine,
                        cours__an=an,
                        creneau=sl,
                        room=precedent.room,
                        copie_travail=target_work_copy)
            # test if lucky
            if len(cp_using_prec) == 1 and cp_using_prec[0] == CP:
                # print "lucky, no change needed"
                continue
            # test if precedent.room is available
            prec_is_unavailable = False
            for r in precedent.room.subrooms.all():
                if RoomPreference.objects.filter(semaine=semaine, an=an, creneau=sl, room=r, valeur=0).exists():
                    prec_is_unavailable = True
                    break
            if prec_is_unavailable:
                # print "room is not available"
                continue
            # test if precedent.room is used for course of the same room_type and swap
            if len(cp_using_prec) == 0:
                CP.room = precedent.room
                CP.save()
                # print "assigned", CP
            elif cp_using_prec[0].cours.room_type == CP.cours.room_type:
                r = CP.room
                CP.room = precedent.room
                sib = cp_using_prec[0]
                sib.room = r
                CP.save()
                sib.save()
                # print "swapped", CP, " with", sib
    print "done"


def basic_swap_version(week, year, copy_a, copy_b=0):
    try:
        tmp_wc = ScheduledCourse \
                     .objects \
                     .filter(cours__semaine=week,
                             cours__an=year) \
                     .aggregate(Max('copie_travail'))['copie_travail__max'] + 1
    except KeyError:
        print 'No scheduled courses'
        return

    for cp in ScheduledCourse.objects.filter(cours__an=year, cours__semaine=week, copie_travail=copy_a):
        cp.copie_travail = tmp_wc
        cp.save()

    for cp in ScheduledCourse.objects.filter(cours__an=year, cours__semaine=week, copie_travail=copy_b):
        cp.copie_travail = copy_a
        cp.save()

    for cp in ScheduledCourse.objects.filter(cours__an=year, cours__semaine=week, copie_travail=tmp_wc):
        cp.copie_travail = copy_b
        cp.save()
