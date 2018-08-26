# coding: utf-8
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


from openpyxl import load_workbook

from base.models import Room, RoomType, RoomGroup, TrainingProgramme, TrainingProgrammeDisplay,\
    Group, Module, GroupType, Period, Time, Day, Slot, CourseType, EdtVersion, UserPreference,\
    CoursePreference

from base.weeks import annee_courante

from misc.check_slots import assign_day_time_numbers

from misc.group_file import generate_group_file

from people.models import FullStaff, SupplyStaff, Tutor

from django.db import IntegrityError

import json

bookname='MyFlOp/IUT_special_apps/ExtractPlanif/database_file_iut.xlsx'

def extract_database_file(bookname=bookname):
    book = load_workbook(filename=bookname, data_only=True)
    tutors_extract(book)
    rooms_extract(book)
    groups_extract(book)
    modules_extract(book)
    slots_extract(book)
    courses_extract(book)
    misc()

def misc():
    for semaine in range(36,53):
        edtv, created = EdtVersion.objects.get_or_create(semaine=semaine, an=annee_courante)
        if created:
            edtv.save()

    for semaine in range(1,27):
        edtv, created = EdtVersion.objects.get_or_create(semaine=semaine, an=annee_courante+1)
        if created:
            edtv.save()

    if not UserPreference.objects.all().exists():
        with open('MyFlOp/IUT_special_apps/ExtractPlanif/Dispos.txt', 'r') as file:
            Dispo = json.load(file)
        translation = {'m': 'lun', 'tu': 'mar', 'w': 'mer', 'th': 'jeu', 'f': 'ven',
              '8':'8h', '9':'9h30', '11':'11h', '14':'14h15', '15':'15h45', '17':'17h15'}
        for sl in Slot.objects.all():
            sl_name = str(sl).split('_')
            nom_creneau = translation[sl_name[0]]+'_'+translation[sl_name[1]]
            for t in Tutor.objects.all():
                if t.username in Dispo:
                    up = UserPreference(user=t, semaine=None, creneau=sl, valeur= Dispo[t.username][nom_creneau])
                    up.save()
        i=0
        for tutor in Tutor.objects.all():
            i=(i+1)%5
            daylist = ['m', 'tu', 'w', 'th', 'f']
            days = [daylist[i], daylist[(i+2)%5]]
            if UserPreference.objects.filter(user=tutor, semaine=None).exists():
                for pref in UserPreference.objects.filter(user=tutor, semaine=None, creneau__jour__day__in = days):
                    pref.valeur = 8
                    pref.save()
    print("Tutor Preferences imported")

    if not CoursePreference.objects.all().exists():
        for ct in CourseType.objects.all():
            for tp in TrainingProgramme.objects.all():
                for sl in Slot.objects.all():
                    course_pref=CoursePreference(course_type=ct, train_prog=tp, creneau=sl)
                    if sl.heure.hours == 8:
                        if sl.jour.day == Day.MONDAY:
                            course_pref.valeur = 1
                        else:
                            course_pref.valeur = 4
                    if sl.heure.hours == 17:
                        if ct.name in ['CM', 'CTRL']:
                            course_pref.valeur = 0
                        elif sl.jour.day == Day.FRIDAY:
                            course_pref.valeur = 1
                        else:
                            course_pref.valeur = 4
                    course_pref.save()

    for U in Tutor.objects.all():
        U.first_name = "prenom_de_" + U.username
        U.last_name = "nom_de_" + U.username
        U.email = "mail_de_" + U.email
        U.set_password("passe")
        U.save()

    PSE = Tutor.objects.get(username='PSE')
    PSE.username = 'MOI'
    PSE.is_staff = True
    PSE.is_superuser = True
    PSE.rights = 6
    PSE.save()
    print("Anonimization done")




def tutors_extract(book):

    sheet = book["Intervenants"]

    INTER_ID_ROW = 3
    id = sheet.cell(row=INTER_ID_ROW, column=1).value

    while id is not None :

        name = sheet.cell(row=INTER_ID_ROW, column=2).value
        last_name = sheet.cell(row=INTER_ID_ROW, column=3).value
        status = sheet.cell(row=INTER_ID_ROW, column=4).value
        email = sheet.cell(row=INTER_ID_ROW, column=5).value
        verif = Tutor.objects.filter(username=id)

        if not verif.exists():

            try:
                if status == "Permanent":
                    tutor = FullStaff(username=id, first_name=name, last_name=last_name, email=email)
                    tutor.set_password("passe")
                    tutor.is_tutor = True
                    tutor.save()

                else:
                    employer = sheet.cell(row=INTER_ID_ROW, column=9).value
                    position = sheet.cell(row=INTER_ID_ROW, column=8).value
                    tutor = SupplyStaff(username=id, password="passe", first_name=name, last_name=last_name,
                                        email=email, employer=employer, position=position)
                    tutor.set_password("passe")
                    tutor.is_tutor = True
                    tutor.save()

            except IntegrityError as ie :
                print("A constraint has not been respected creation the Professor : \n", ie)
                pass

        INTER_ID_ROW += 1
        id = sheet.cell(row=INTER_ID_ROW, column=1).value

    print("Tutors extraction done")


def rooms_extract(book):

    sheet = book['Salles']
    ######################## Creating RoomTypes ####################################

    SALLES_CAT_ROW = 20
    idCat = sheet.cell(row=SALLES_CAT_ROW, column=5).value

    while idCat is not None :

        verif = RoomType.objects.filter(name=idCat)

        if not verif.exists():

            try:
                roomType = RoomType(name=idCat)
                roomType.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the RoomType %s : \n" %idCat, ie)
                pass

        SALLES_CAT_ROW+=1
        idCat = sheet.cell(row=SALLES_CAT_ROW, column=5).value

    ######################## Creating Rooms ####################################

    SALLES_ROOM_ROW = 3
    idRoom = sheet.cell(row=SALLES_ROOM_ROW, column=1).value


    while idRoom is not None :

        verif = Room.objects.filter(name=idRoom)

        if not verif.exists():

            try:

                roomG = RoomGroup(name=idRoom)
                roomG.save()

                room = Room(name=idRoom)
                room.save()
                room.subroom_of.add(roomG)
                room.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the Room %s : \n" %idRoom, ie)
                pass

        SALLES_ROOM_ROW += 1
        idRoom = sheet.cell(row=SALLES_ROOM_ROW, column=1).value

    ######################## Creating RoomGroups ####################################

    SALLES_ROOMG_ROW = 3
    idRoomGroup = sheet.cell(row=SALLES_ROOMG_ROW, column=2).value

    while idRoomGroup is not None :

        verif = RoomGroup.objects.filter(name=idRoomGroup)

        if not verif.exists():

            try:

                roomG = RoomGroup(name=idRoomGroup)
                roomG.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the RoomGroup %s : \n" %idRoomGroup, ie)
                pass

        SALLES_ROOMG_ROW += 1
        idRoomGroup = sheet.cell(row=SALLES_ROOMG_ROW, column=2).value

    ######################## Filling the RoomGroups with Rooms ####################################

    SALLES_GROUPS_ROW = 4
    idGroup = sheet.cell(row=SALLES_GROUPS_ROW, column=5).value

    while idGroup is not None :

        SALLES_GROUPS_COL = 3
        idRoom = sheet.cell(row=SALLES_GROUPS_ROW, column=SALLES_GROUPS_COL).value


        while idRoom is not None :

            R = Room.objects.get(name=idRoom)
            R.subroom_of.add(RoomGroup.objects.get(name=idGroup))
            R.save()
            SALLES_GROUPS_COL += 1
            idRoom = sheet.cell(row=SALLES_GROUPS_ROW, column=SALLES_GROUPS_COL).value

        SALLES_GROUPS_ROW += 1
        idGroup = sheet.cell(row=SALLES_GROUPS_ROW, column=5).value

    ######################## Giving a RoomType to each RoomGroup ####################################

    SALLES_CAT_ROW = 20
    idCat = sheet.cell(row=SALLES_CAT_ROW, column=5).value

    while idCat is not None :

        ROOMGROUP_COL = 6
        idRoomGroup = sheet.cell(row=SALLES_CAT_ROW, column=ROOMGROUP_COL).value

        while idRoomGroup is not None :

            RoomGroup.objects.get(name=idRoomGroup).types.add(RoomType.objects.get(name=idCat))
            ROOMGROUP_COL += 1
            idRoomGroup = sheet.cell(row=SALLES_CAT_ROW, column=ROOMGROUP_COL).value

        SALLES_CAT_ROW += 1
        idCat = sheet.cell(row=SALLES_CAT_ROW, column=5).value

    print("Rooms extraction done")

# groups_extract
# Creates the groups, the training programs, and
# and fills the groups with their parent groups

def groups_extract(book):

    sheet = book['Groupes']

    ######################## Creating the TrainingPrograms ####################################

    TP_ROW = 3
    TP_COL = 13

    idTP = sheet.cell(row=TP_ROW, column=TP_COL).value

    while idTP is not None:

        verif = TrainingProgramme.objects.filter(abbrev=idTP)

        if not verif.exists():

            nameTP = sheet.cell(row=TP_ROW, column=TP_COL + 1).value

            try:
                trainingProg = TrainingProgramme(name=nameTP, abbrev=idTP)
                trainingProg.save()
            except IntegrityError as ie:
                print("A constraint has not been respected creating the TrainingProgramme %s : \n" % idTP, ie)
                pass

        TP_ROW += 1
        idTP = sheet.cell(row=TP_ROW, column=TP_COL).value

    ######################## Creating the GroupTypes ####################################

    GT_ROW = 17

    idGroupType = sheet.cell(row=GT_ROW, column=13).value

    while idGroupType is not None:

        verif = GroupType.objects.filter(name=idGroupType)

        if not verif.exists():

            try:

                gt = GroupType(name=idGroupType)
                gt.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the GroupType %s : \n" % idGroupType, ie)
                pass

        GT_ROW += 1
        idGroupType = sheet.cell(row=GT_ROW, column=13).value


    ######################## Creating the Groups ####################################

    GROUP_ROW = 3

    idGroup = sheet.cell(row=GROUP_ROW, column=1).value

    while idGroup is not None:

        tpGr = sheet.cell(row=GROUP_ROW, column=2).value
        verif = Group.objects.filter(nom=idGroup, train_prog__abbrev=tpGr)

        if not verif.exists():

            try:

                tpGr = sheet.cell(row=GROUP_ROW, column=2).value
                tpGroup = TrainingProgramme.objects.get(abbrev=tpGr)

                gt = sheet.cell(row=GROUP_ROW, column=5).value
                groupType = GroupType.objects.get(name=gt)

                group = Group(nom=idGroup, size=0, train_prog=tpGroup, type=groupType)
                group.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the Group %s : \n" % idGroup, ie)
                pass

        GROUP_ROW += 1
        idGroup = sheet.cell(row=GROUP_ROW, column=1).value


    ######################## Filling the Groups with their parent groups ####################################

    GROUP_ROW = 3

    idGroup = sheet.cell(row=GROUP_ROW, column=1).value

    while idGroup is not None:

        tpGr = sheet.cell(row=GROUP_ROW, column=2).value
        p_group = sheet.cell(row=GROUP_ROW, column=3).value
        p_group2 = sheet.cell(row=GROUP_ROW, column=4).value

        if p_group is not None:

            parent_group = Group.objects.get(nom=p_group, train_prog__abbrev=tpGr)

            group = Group.objects.get(nom=idGroup, train_prog__abbrev=tpGr)

            group.parent_groups.add(parent_group)

            group.save()

            if p_group2 is not None:

                parent_group = Group.objects.get(nom=p_group2, train_prog__abbrev=tpGr)

                group = Group.objects.get(nom=idGroup, train_prog__abbrev=tpGr)

                group.parent_groups.add(parent_group)

                group.save()

        GROUP_ROW += 1
        idGroup = sheet.cell(row=GROUP_ROW, column=1).value

######################## Defining basic groups ####################################

    for g in Group.objects.all():

        isbasic = True

        for g1 in Group.objects.all():

            if g in g1.parent_groups.all():

                isbasic = False

        g.basic = isbasic
        g.save()

######################## Defining Periods ####################################

    PERIOD_ROW = 12

    id_per = sheet.cell(row=PERIOD_ROW, column=7).value

    while id_per is not None:

        verif = Period.objects.filter(name = id_per)

        if not verif.exists():

            s_week = int(sheet.cell(row=PERIOD_ROW, column=8).value)
            e_week = int(sheet.cell(row=PERIOD_ROW, column=9).value)

            try:

                period = Period(name=id_per, starting_week=s_week, ending_week=e_week)
                period.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the Period %s : \n" % id_per, ie)
                pass

        PERIOD_ROW += 1
        id_per = sheet.cell(row=PERIOD_ROW, column=7).value

    for tp in TrainingProgramme.objects.all():
        if not TrainingProgrammeDisplay.objects.filter(training_programme=tp).exists():
            if tp.abbrev =='INFO1':
                tpd = TrainingProgrammeDisplay(training_programme=tp, row=0)
            else:
                tpd = TrainingProgrammeDisplay(training_programme=tp, row=1)
            tpd.save()

    generate_group_file()

    print("Groups extraction done")


def modules_extract(book):

    sheet = book["Modules"]

    MODULE_ROW=3

    idMod=sheet.cell(row=MODULE_ROW, column=1).value


    while idMod is not None:

        tpMod = sheet.cell(row=MODULE_ROW, column=4).value
        period = sheet.cell(row=MODULE_ROW, column=6).value
        verif = Module.objects.filter(abbrev=idMod, train_prog__abbrev=tpMod, period__name=period)


        if not verif.exists():

            codeMod = sheet.cell(row=MODULE_ROW, column=2).value
            nameMod = sheet.cell(row=MODULE_ROW, column=3).value
            tpMod = sheet.cell(row=MODULE_ROW, column=4).value
            profMod = sheet.cell(row=MODULE_ROW, column=5).value
            tpModule = TrainingProgramme.objects.get(abbrev=tpMod)
            profesMod = Tutor.objects.get(username=profMod)
            periodMod = Period.objects.get(name=period)

            try:

                module = Module(nom=nameMod, abbrev=idMod, ppn=codeMod, train_prog=tpModule, head=profesMod, period=periodMod)
                module.save()

            except IntegrityError as ie:
                print("A constraint has not been respected creating the Module %s : \n" % idMod, ie)
                pass

        MODULE_ROW+=1

        idMod=sheet.cell(row=MODULE_ROW, column=1).value

    print("Modules extraction done")

def slots_extract(book):

    sheet = book["Creneaux"]

    answer = sheet.cell(row=3, column=12).value
    for d in Day.CHOICES[:5]:
        day, created = Day.objects.get_or_create(day=d[0])
    if created:
        day.save()

    if answer == "Oui":
        print("'normal' slots imported")
        default_times=[(8,0),(9,30),(11,0),(14,15),(15,45),(17,15)]
        for hours,minutes in default_times:
            time, created = Time.objects.get_or_create(hours=hours, minutes=minutes)
            if created:
                time.save()
            for day in Day.objects.all():
                slot, created = Slot.objects.get_or_create(duration=90, jour=day, heure=time)
                if created:
                    slot.save()
        assign_day_time_numbers()
        return None

    CRENEAU_ROW=3

    dura = sheet.cell(row=CRENEAU_ROW, column=1).value

    while dura is not None:

        TIME_COL = 3

        day = sheet.cell(row=CRENEAU_ROW, column=2).value
        hour = sheet.cell(row=CRENEAU_ROW, column=TIME_COL).value

        if day == "Tous les jours":
            days = [d[0] for d in Day.CHOICES[:5]]
        elif day == "Lundi":
            days = [Day.MONDAY]
        elif day == "Mardi":
            days = [Day.TUESDAY]
        elif day == "Mercredi":
            days = [Day.WEDNESDAY]
        elif day == "Jeudi":
            days = [Day.THURSDAY]
        elif day == "Vendredi":
            days = [Day.FRIDAY]


        while hour is not None:

            try:

                time = hour.split('h')
                hours = int(time[0])

                if time[1] != "":

                    minutes = int(time[1])

                else:

                    minutes = 0
                slotTime, created = Time.objects.get_or_create(hours=hours, minutes=minutes)

                if created:

                    slotTime.save()

                for day in days:

                    slot, created = Slot.objects.get_or_create(duration=dura,
                                                               jour=Day.objects.get(day=day),
                                                               heure=slotTime)
                    if created:

                        slot.save()

            except IntegrityError as ie:

                print("A constraint has not been respected creating the Slot %s : \n" % dura, ie)
                pass

            TIME_COL += 1
            hour = sheet.cell(row=CRENEAU_ROW, column=TIME_COL).value

        CRENEAU_ROW += 1
        dura = sheet.cell(row=CRENEAU_ROW, column=TIME_COL).value

    assign_day_time_numbers()

    print("Slots extraction done")

def courses_extract(book):

    sheet = book['Cours']

    TYPE_ROW = 3

    idType = sheet.cell(row=TYPE_ROW, column=1).value

    while idType is not None:

        TYPE_COL = 2

        verif = CourseType.objects.filter(name=idType)

        if not verif.exists():

            try:

                course = CourseType(name=idType)
                course.save()

            except IntegrityError as ie:

                print("A constraint has not been respected creating the CourseType %s : \n" % idType, ie)
                pass

            idGroup = sheet.cell(row=TYPE_ROW, column=TYPE_COL).value

            while idGroup is not None:

                group = GroupType.objects.get(name=idGroup)
                course.group_types.add(group)
                course.save()

                TYPE_COL += 1
                idGroup = sheet.cell(row=TYPE_ROW, column=TYPE_COL).value

        TYPE_ROW += 1
        idType = sheet.cell(row=TYPE_ROW, column=1).value

    print("Courses' types extraction done")



def displayInfo():

    print("The Professors are : ")

    for p in Tutor.objects.all():

        print(p.username, " : ", p.first_name, " ", p.last_name.upper())

        if p.status == Tutor.SUPP_STAFF :
            print("Qualite : ", p.qualite)
            print("Employer : ", p.employer)
            print("Status : SupplyStaff")
        else:
            print("Status : FullStaff")

        print("e-mail : ", p.email, "\n")

    print("------------------")

    print("The Rooms are : ")

    for r in Room.objects.all():

        print(r.name, ", subroom of : ")

        for sub in r.subroom_of.all():

            print(sub)

    print("---")

    print("The Room groups are : ")

    for rg in RoomGroup.objects.all():

        print(rg.name, ", types : ")

        for t in rg.types.all():

            print("| ", t, " |")

    print("---")

    print("The Room types are : ")

    for rt in RoomType.objects.all():

        print(rt)

    print("------------------")

    print("The Training programs are : ")

    for tp in TrainingProgramme.objects.all():

        print(tp.abbrev, " : ", tp)

    print("---")

    print("The Group types are : ")

    for gt in GroupType.objects.all():

        print(gt)

    print("---")

    print("The Groups are : ")

    for g in Group.objects.all():

        print(g, " : ")
        print(" - size : ", g.size)
        print(" - type : ", g.type)
        print(" - basic : ", g.basic)

        print(" - parent groups : ")
        for i in g.ancestor_groups():
            print(i)

    print("------------------")

    print("The Modules are : ")

    for m in Module.objects.all():

        print(m, " : ", m.nom, " - ", m.ppn)
        print("- head : ", m.head)
        print("- training program : ", m.train_prog)
        print("- starting week : ", m.period.starting_week)
        print("- ending week : ", m.period.ending_week)

    print("------------------")

    print("The Slots are : ")

    for s in Slot.objects.all():

        print(s, " ", s.duration)
