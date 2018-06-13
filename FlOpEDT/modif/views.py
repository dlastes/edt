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

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from django.core.cache import cache

from django.db import transaction

import json

from .forms import ContactForm

from .models import Course, UserPreference, ScheduledCourse, EdtVersion, \
    CourseModification, Slot, Day, Time, RoomGroup, PlanningModification, \
    Regen, BreakingNews, Tutor
# Prof,

from .admin import CoursResource, DispoResource, \
    CoursPlaceResource, BreakingNewsResource

from weeks import *

from collections import namedtuple

from itertools import chain

from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView

# Texte de l'image
# # randomVar = randint(0, 2)
randomVar = 1

if randomVar == 0:
    imgtxt = "\"Qui veut faire les EDT cette année ?\" ... Fl" \
             "<span id=\"flopRed\">Op</span> !"
elif randomVar == 1:
    imgtxt = "Créateur d'emploi du temps <span id=\"flopPasRed\">Fl" \
             "</span>exible et <span id=\"flopRed\">Op</span>enSource"
elif randomVar == 2:
    imgtxt = "Et votre emploi du temps fera un " \
             "<span id=\"flopRedDel\">flop</span> carton !"

# <editor-fold desc="FAVICON">
# ----------
# FAVICON
# ----------


fav_regexp = r'^(?P<fav>(favicon.ico)|(site\.webmanifest)' \
             r'|(browserconfig\.xml)|(safari-pinned-tab.svg)' \
             r'|(mstile.*\.png)|(favicon.*\.png)|(android-chrome.*\.png)' \
             r'|(apple-touch-icon.*\.png))$'


def favicon(req, fav):
    return RedirectView.as_view(
        url=staticfiles_storage.url('modif/img/favicons/' + fav),
        permanent=False)(req)


# </editor-fold desc="FAVICON">


# <editor-fold desc="VIEWERS">
# ----------
# VIEWERS
# ----------


def edt(req, semaine, an, splash_id=0):
    semaine, an = clean_week(semaine, an)
    promo = clean_train_prog(req)

    if req.GET:
        copie = req.GET.get('cop', '0')
        copie = int(copie)
        gp = req.GET.get('gp', '')
    else:
        copie = 0
        gp = ''

    # une_salle = RoomGroup.objects.all()[1].name
    une_salle = 'salle?'

    if req.user.is_authenticated():
        name_usr = req.user.username
        try:
            rights_usr = req.user.rights
        except ObjectDoesNotExist:
            rights_usr = 0
    else:
        name_usr = ''
        rights_usr = 0

    return render(req, 'modif/show-edt.html',
                  {'all_weeks': week_list(),
                   'semaine': semaine,
                   'an': an,
                   'jours': num_days(an, semaine),
                   'promo': promo,
                   'une_salle': une_salle,
                   'copie': copie,
                   'gp': gp,
                   'name_usr': name_usr,
                   'rights_usr': rights_usr,
                   'splash_id': splash_id,
                   'image': imgtxt})


def edt_light(req, semaine, an):
    semaine, an = clean_week(semaine, an)
    promo = clean_train_prog(req)

    if req.GET:
        svg_h = req.GET.get('svg_h', '640')
        svg_w = req.GET.get('svg_w', '1370')
        gp_h = req.GET.get('gp_h', '40')
        gp_w = req.GET.get('gp_w', '30')
        svg_top_m = req.GET.get('top_m', '40')

        svg_h = int(svg_h)
        svg_w = int(svg_w)
        gp_h = int(gp_h)
        gp_w = int(gp_w)
        svg_top_m = int(svg_top_m)

    else:
        svg_h = 640
        svg_w = 1370
        gp_h = 40
        gp_w = 30
        svg_top_m = 40

    une_salle = "salle?"  # RoomGroup.objects.all()[0].name

    return render(req, 'modif/show-edt-light.html',
                  {'all_weeks': week_list(),
                   'semaine': semaine,
                   'an': an,
                   'jours': num_days(an, semaine),
                   'une_salle': une_salle,
                   'tv_svg_h': svg_h,
                   'tv_svg_w': svg_w,
                   'tv_gp_h': gp_h,
                   'tv_gp_w': gp_w,
                   'promo': promo,
                   'tv_svg_top_m': svg_top_m,
                   'image': imgtxt})


@login_required
def stype(req):
    err = ''
    if req.method == 'GET':
        return render(req,
                      'modif/show-stype.html',
                      {'date_deb': current_week(),
                       'date_fin': current_week(),
                       'name_usr': req.user.username,
                       'err': err,
                       'annee_courante': annee_courante,
                       'image': imgtxt})
    elif req.method == 'POST':
        if 'apply' in req.POST.keys():
            print req.POST['se_deb']
            date_deb = {'semaine': req.POST['se_deb'],
                        'an': req.POST['an_deb']}
            date_fin = {'semaine': req.POST['se_fin'],
                        'an': req.POST['an_fin']}
            if date_deb['an'] < date_fin['an'] or \
                    (date_deb['an'] == date_fin['an']
                     and date_deb['semaine'] <= date_fin['semaine']):
                print req.POST['apply']
            else:
                date_deb = current_week()
                date_fin = current_week()
                err = "Problème : seconde semaine avant la première"

        else:
            date_deb = current_week()
            date_fin = current_week()

            print req.POST['save']

        return render(req,
                      'modif/show-stype.html',
                      {'date_deb': date_deb,
                       'date_fin': date_fin,
                       'name_usr': req.user.username,
                       'err': err,
                       'annee_courante': annee_courante,
                       'image': imgtxt})


def aide(req):
    return render(req, 'modif/aide.html', {
        'image': imgtxt})


@login_required
def decale(req):
    if req.method != 'GET':
        return render(req, 'modif/aide.html', {})

    semaine_init = req.GET.get('s', '-1')
    an_init = req.GET.get('a', '-1')
    liste_profs = []
    for p in Tutor.objects.all().order_by('username'):
        liste_profs.append(p.username.encode('utf8'))

    return render(req, 'modif/show-decale.html',
                  {'all_weeks': week_list(),
                   'semaine_init': semaine_init,
                   'an_init': an_init,
                   'profs': liste_profs,
                   'image': imgtxt})


# </editor-fold desc="VIEWERS">


# <editor-fold desc="FETCHERS">
# ----------
# FETCHERS
# ----------


def fetch_cours_pl(req):
    print req
    if req.GET:
        semaine = req.GET.get('s', '')
        an = req.GET.get('a', '')
        num_copie = req.GET.get('c', '')
        semaine = int(semaine)
        an = int(an)
        num_copie = int(num_copie)
        ok = False
        version = 0
        dataset = None
        while not ok:
            if num_copie == 0:
                edtversion, created = EdtVersion.objects \
                    .get_or_create(semaine=semaine,
                                   an=an,
                                   defaults={'version': 0})
                version = edtversion.version
            dataset = CoursPlaceResource() \
                .export(ScheduledCourse.objects \
                        .filter(cours__semaine=semaine,
                                cours__an=an,
                                copie_travail=num_copie)
                        .order_by('creneau__jour',
                                  'creneau__heure'))  # all())#
            ok = num_copie != 0 \
                 or (version == EdtVersion.objects
                     .get(semaine=semaine, an=an).version)
        if dataset is None:
            raise Http404("What are you trying to do?")
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['version'] = version
        response['semaine'] = semaine
        response['an'] = an
        response['jours'] = str(num_days(an, semaine))
        response['num_copie'] = num_copie
        try:
            regen = str(Regen.objects.get(semaine=semaine, an=an))
        except ObjectDoesNotExist:
            regen = 'I'
        response['regen'] = regen
        if req.user.is_authenticated():
            response['reqDispos'] = Course \
                                        .objects \
                                        .filter(tutor=req.user,
                                                semaine=semaine,
                                                an=an) \
                                        .count() * 2
            week_av = UserPreference \
                .objects \
                .filter(user=req.user,
                        semaine=semaine,
                        an=an)
            if not week_av.exists():
                response['filDispos'] = UserPreference \
                    .objects \
                    .filter(user=req.user,
                            semaine=None,
                            valeur__gte=1) \
                    .count()
            else:
                response['filDispos'] = week_av \
                    .filter(valeur__gte=1) \
                    .count()
        else:
            response['reqDispos'] = -1
            response['filDispos'] = -1
        return response


def fetch_cours_pp(req):
    print req
    if req.GET:
        semaine = req.GET.get('s', '')
        an = req.GET.get('a', '')
        num_copie = req.GET.get('c', '')
        semaine = int(semaine)
        an = int(an)
        num_copie = int(num_copie)
        dataset = CoursResource() \
            .export(Course
                    .objects
                    .filter(semaine=semaine,
                            an=an)
                    .exclude(pk__in=ScheduledCourse
                             .objects
                             .filter(copie_travail=num_copie)
                             .values('cours')))
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['semaine'] = semaine
        response['an'] = an

        return response


# @login_required
def fetch_dispos(req):
    print req
    if req.GET:
        if req.user.is_authenticated():
            print "================"
            semaine = req.GET.get('s', '')
            an = req.GET.get('a', '')

            busy_inst = Course.objects.filter(semaine=semaine,
                                              an=an) \
                .distinct('tutor') \
                .values_list('tutor')

            busy_inst = list(chain(busy_inst, [req.user]))

            week_avail = UserPreference.objects \
                .filter(semaine=semaine,
                        an=an,
                        user__in=busy_inst) \
                .order_by('user')

            default_avail = UserPreference.objects \
                .exclude(user__in \
                             =week_avail \
                         .distinct('user') \
                         .values_list('user')) \
                .filter(semaine=None,
                        user__in=busy_inst) \
                .order_by('user')

            dataset = DispoResource() \
                .export(list(chain(week_avail,
                                   default_avail)))  # all())#
            response = HttpResponse(dataset.csv,
                                    content_type='text/csv')
            response['semaine'] = semaine
            response['an'] = an
            return response
        else:
            return HttpResponse(u"Pas connecté", status=500)
    else:
        return HttpResponse("Pas GET", status=500)


@login_required
def fetch_stype(req):
    # if req.method == 'GET':
    dataset = DispoResource() \
        .export(UserPreference.objects \
                .filter(semaine=None,
                        user=req.user))  # all())#
    response = HttpResponse(dataset.csv, content_type='text/csv')
    return response
    # else:
    #    return HttpResponse("Pas GET",status=500)


def fetch_decale(req):
    if not req.is_ajax() or req.method != "GET":
        return HttpResponse("KO")

    semaine = int(req.GET.get('s', '0'))
    an = int(req.GET.get('a', '0'))
    module = req.GET.get('m', '')
    prof = req.GET.get('p', '')
    groupe = req.GET.get('g', '')

    liste_cours = []
    liste_module = []
    liste_prof = []
    liste_prof_module = []
    liste_groupe = []

    if an > 0 and semaine > 0:
        liste_jours = num_days(an, semaine)
    else:
        liste_jours = []

    cours = filt_p(filt_g(filt_m(filt_sa(semaine, an), module), groupe), prof)

    for c in cours:
        try:
            cp = ScheduledCourse.objects.get(cours=c,
                                             copie_travail=0)
            j = cp.creneau.jour.no
            h = cp.creneau.heure.no
        except ObjectDoesNotExist:
            j = -1
            h = -1
        if c.tutor is not None:
            liste_cours.append({'i': c.id,
                                'm': c.module.nom,
                                'p': c.tutor.username,
                                'g': c.groupe.nom,
                                'j': j,
                                'h': h})

    cours = filt_p(filt_g(filt_sa(semaine, an), groupe), prof) \
        .order_by('module__nom') \
        .distinct('module__nom')
    for c in cours:
        liste_module.append(c.module.nom)

    cours = filt_g(filt_m(filt_sa(semaine, an), module), groupe) \
        .order_by('tutor__username') \
        .distinct('tutor__username')
    for c in cours:
        if c.tutor is not None:
            liste_prof.append(c.tutor.username)

    if module != '':
        cours = filt_m(Course.objects, module) \
            .order_by('tutor__username') \
            .distinct('tutor__username')
        for c in cours:
            if c.tutor is not None:
                liste_prof_module.append(c.tutor.username)

    cours = filt_p(filt_m(filt_sa(semaine, an), module), prof) \
        .distinct('groupe')
    for c in cours:
        liste_groupe.append(c.groupe.nom)

    return JsonResponse({'cours': liste_cours,
                         'modules': liste_module,
                         'profs': liste_prof,
                         'profs_module': liste_prof_module,
                         'groupes': liste_groupe,
                         'jours': liste_jours})


def fetch_bknews(req):
    week = int(req.GET.get('w', '0'))
    year = int(req.GET.get('y', '0'))

    dataset = BreakingNewsResource() \
        .export(BreakingNews.objects.filter(year=year,
                                            week=week))
    response = HttpResponse(dataset.json,
                            content_type='text/json')
    response['semaine'] = week
    response['an'] = year
    return response


# </editor-fold desc="FETCHERS">

# <editor-fold desc="CHANGERS">
# ----------
# CHANGERS
# ----------


@login_required
def edt_changes(req):
    bad_response = HttpResponse("KO")
    good_response = HttpResponse("OK")

    impacted_inst = set()

    msg = 'Notation : (numero_semaine, numero_annee, ' \
          + 'numero_jour, numero_creneau)\n\n'

    print req
    if req.is_ajax():
        if req.method == "POST":
            semaine = req.GET.get('s', '')
            an = req.GET.get('a', '')
            work_copy = req.GET.get('c', '')
            semaine = int(semaine)
            an = int(an)
            work_copy = int(work_copy)
            version = None

            print req.body
            q = json.loads(req.body,
                           object_hook
                           =lambda d: namedtuple('X', d.keys())(*d.values())
                           )

            if work_copy == 0:
                edt_version, created = EdtVersion.objects \
                    .get_or_create(semaine=semaine,
                                   an=an,
                                   defaults={'version': 0})
                version = edt_version.version

            if work_copy != 0 or q.v == version:
                with transaction.atomic():
                    if work_copy == 0:
                        edt_version = EdtVersion \
                            .objects \
                            .select_for_update() \
                            .get(semaine=semaine, an=an)
                    for a in q.tab:
                        non_place = False
                        co = Course.objects.get(id=a.id)
                        try:
                            cp = ScheduledCourse.objects.get(cours=co,
                                                             copie_travail=work_copy)
                        except ObjectDoesNotExist:
                            non_place = True
                            cp = ScheduledCourse(cours=co,
                                                 copie_travail=work_copy)

                        m = CourseModification(cours=co,
                                               version_old=q.v,
                                               initiator=req.user)
                        # old_day = a.day.o
                        # old_slot = a.slot.o
                        new_day = a.day.n
                        new_slot = a.slot.n
                        old_room = a.room.o
                        new_room = a.room.n

                        if non_place:
                            # old_day = new_day
                            # old_slot = new_slot
                            if a.room.n is None:
                                new_room = old_room

                        if new_day is not None:
                            try:
                                cren_n = Slot \
                                    .objects \
                                    .get(jour=Day.objects \
                                         .get(no=new_day),
                                         heure \
                                             =Time \
                                         .objects \
                                         .get(no=new_slot))
                            except ObjectDoesNotExist:
                                bad_response['reason'] \
                                    = u"Problème : créneau " + new_day
                                return bad_response
                            if non_place:
                                cp.creneau = cren_n
                            m.creneau_old = cp.creneau
                            cp.creneau = cren_n
                            print cren_n
                            print m
                            print cp
                        if new_room is not None:
                            try:
                                sal_n = RoomGroup.objects.get(name=new_room)
                            except ObjectDoesNotExist:
                                if new_room == 'salle?':
                                    bad_response['reason'] \
                                        = u'Oublié de trouver une salle ' \
                                          u'pour un cours ?'
                                else:
                                    bad_response['reason'] = \
                                        u"Problème : salle " + new_room \
                                        + u" inconnue"
                                return bad_response

                            if non_place:
                                cp.room = sal_n
                            m.room_old = cp.room
                            cp.room = sal_n
                        if a.week.n is not None:
                            m.semaine_old = a.week.o
                            m.an_old = a.year.o
                            cp.cours.semaine = a.week.n
                            cp.cours.an = a.year.n
                        cp.save()
                        if work_copy == 0:
                            m.save()

                        if a.week.n or a.year.n or a.day.n or a.slot.n:
                            msg += str(co) + '\n'
                            impacted_inst.add(co.tutor.username)

                            msg += u'(' + str(a.week.o) + u', ' \
                                   + str(a.year.o) + u', ' \
                                   + str(a.day.o) + u', ' \
                                   + str(a.slot.o) + u')'
                            msg += u' -> ('
                            if a.week.n:
                                msg += str(a.week.n)
                            else:
                                msg += '-'
                            msg += ', '
                            if a.year.n:
                                msg += str(a.year.n)
                            else:
                                msg += '-'
                            msg += ', '
                            if a.day.n:
                                msg += str(a.day.n)
                            else:
                                msg += '-'
                            msg += ', '
                            if a.slot.n:
                                msg += str(a.slot.n)
                            else:
                                msg += '-'
                            msg += ')\n\n'

                    if work_copy == 0:
                        edt_version.version += 1
                        edt_version.save()

                subject = u'[Modif sur tierce] ' + req.user.username \
                          + u' a déplacé '
                for inst in impacted_inst:
                    if inst is not req.user.username:
                        subject += inst + ' '

                if len(impacted_inst) > 0 and work_copy == 0:
                    if len(impacted_inst) > 1 \
                            or req.user.username not in impacted_inst:
                        send_mail(
                            subject,
                            msg,
                            'edt@iut-blagnac',
                            ['edt.info.iut.blagnac@gmail.com']
                        )

                return good_response
            else:
                bad_response['reason'] = "Version: " \
                                         + str(version) \
                                         + " VS " \
                                         + str(q.v)
                return bad_response
        else:
            bad_response['reason'] = "Non POST"
            return bad_response
    else:
        bad_response['reason'] = "Non ajax"
        return bad_response


@login_required
def dispos_changes(req):
    bad_response = HttpResponse("KO")
    good_response = HttpResponse("OK")
    if req.is_ajax():
        if req.method == "POST":
            try:
                semaine = req.GET.get('s', '')
                an = req.GET.get('a', '')
                semaine = int(semaine)
                an = int(an)
            except ValueError:
                bad_response['reason'] \
                    = u"Problème semaine ou année."
                return bad_response
                
            usr_change = req.GET.get('u', '')
            if usr_change == '':
                usr_change = req.user.username

            # Default week at None
            if semaine == 0 or an == 0:
                semaine = None
                an = None

            print req.body
            q = json.loads(req.body,
                           object_hook=lambda d:
                           namedtuple('X', d.keys())(*d.values()))

            prof = None
            try:
                prof = Tutor.objects.get(username=usr_change)
            except ObjectDoesNotExist:
                bad_response['reason'] \
                    = u"Problème d'utilisateur."
                return bad_response

            if prof != req.user and req.user.rights >> 1 % 2 == 0:
                bad_response['reason'] \
                    = u'Non autorisé, réclamez plus de droits.'
                return bad_response

            print q

            # if no preference was present for this week, first copy the
            # default availabilities
            if not UserPreference.objects.filter(user=prof,
                                                 semaine=semaine,
                                                 an=an).exists():
                for c in Slot.objects.all():
                    def_dispo, created = UserPreference \
                        .objects \
                        .get_or_create(
                        user=prof,
                        semaine=None,
                        creneau=c,
                        defaults={'valeur':
                                      0})
                    new_dispo = UserPreference(user=prof,
                                               semaine=semaine,
                                               an=an,
                                               creneau=c,
                                               valeur=def_dispo.valeur)
                    new_dispo.save()

            for a in q:
                print a
                cr = Slot.objects \
                    .get(jour=Day.objects.get(no=a.day),
                         heure=Time.objects.get(no=a.hour))
                if cr is None:
                    bad_response['reason'] = "Creneau pas trouve"
                    return bad_response
                di, didi = UserPreference \
                    .objects \
                    .update_or_create(user=prof,
                                      semaine=semaine,
                                      an=an,
                                      creneau=cr,
                                      defaults={'valeur': a.val})
                print di
                print didi
            return good_response
        else:
            bad_response['reason'] = "Non POST"
            return bad_response
    else:
        bad_response['reason'] = "Non Ajax"
        return bad_response


@login_required
def decale_changes(req):
    bad_response = HttpResponse("KO")
    good_response = HttpResponse("OK")
    print req

    if not req.is_ajax():
        bad_response['reason'] = "Non ajax"
        return bad_response

    if req.method != "POST":
        bad_response['reason'] = "Non POST"
        return bad_response

    print req.body
    q = json.loads(req.body,
                   object_hook=lambda d:
                   namedtuple('X', d.keys())(*d.values()))

    a = q.new

    for c in q.liste:
        # try:
        if c.j != -1 and c.h != -1:
            cours_place = ScheduledCourse \
                .objects \
                .get(cours__id=c.i,
                     copie_travail=0)
            cours = cours_place.cours
            cours_place.delete()
        else:
            cours = Course.objects.get(id=c.i)
            # note: add copie_travail in Cours might be of interest

        pm = PlanningModification(cours=cours,
                                  semaine_old=cours.semaine,
                                  an_old=cours.an,
                                  tutor_old=cours.tutor,
                                  initiator=req.user)
        pm.save()

        cours.semaine = a.ns
        cours.an = a.na
        if a.na != 0:
            # cours.prof=User.objects.get(username=a.np)
            cours.tutor = Tutor.objects.get(username=a.np)
        cours.save()

        # flush the whole cache
        cache.clear()

    return good_response


# </editor-fold desc="CHANGERS">

# <editor-fold desc="EMAILS">
# ---------
# E-MAILS
# ---------


def contact(req):
    ack = ''
    if req.method == 'POST':
        form = ContactForm(req.POST)
        if form.is_valid():
            dat = form.cleaned_data
            recip_send = [Tutor.objects.get(username=
                                            dat.get("recipient")).email,
                          dat.get("sender")]
            try:
                send_mail(
                    '[EdT IUT Blagnac] ' + dat.get("subject"),
                    u"(Cet e-mail vous a été envoyé depuis le site des emplois"
                    u" du temps de l'IUT de Blagnac)\n\n"
                    + dat.get("message"),
                    dat.get("sender"),
                    recip_send,
                )
            except:
                ack = u'Envoi du mail impossible !'
                return render(req, 'modif/contact.html',
                              {'form': form,
                               'ack': ack,
                               'image': imgtxt})

            return edt(req, None, None, 1)
    else:
        init_mail = ''
        if req.user.is_authenticated():
            init_mail = req.user.email
        form = ContactForm(initial={
            'sender': init_mail})
    return render(req, 'modif/contact.html',
                  {'form': form,
                   'ack': ack,
                   'image': imgtxt})


# </editor-fold desc="EMAILS">

# <editor-fold desc="HELPERS">
# ---------
# HELPERS
# ---------


def clean_train_prog(req):
    if req.GET:
        promo = req.GET.get('promo', '0')
        try:
            promo = int(promo)
        except ValueError:
            promo = 0
        if promo not in [1, 2, 3]:
            promo = 0
    else:
        promo = 0
    return promo


def clean_week(week, year):
    if week is None or year is None:
        today = current_week()
        week = today['semaine']
        year = today['an']
    else:
        try:
            week = int(week)
            year = int(year)
        except ValueError:
            today = current_week()
            week = today['semaine']
            year = today['an']
    return week, year


def filt_m(r, module):
    if module != '':
        r = r.filter(module__nom=module)
    return r


def filt_p(r, prof):
    if prof != '':
        r = r.filter(tutor__username=prof)
    return r


def filt_g(r, groupe):
    if groupe != '':
        r = r.filter(groupe__nom=groupe)
    return r


def filt_sa(semaine, an):
    return Course.objects.filter(semaine=semaine,
                                 an=an)

# </editor-fold desc="HELPERS">
