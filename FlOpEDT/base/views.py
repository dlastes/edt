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

import json
from collections import namedtuple
from itertools import chain
from random import randint
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.db import transaction
from django.http import HttpResponse, Http404, JsonResponse, HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView
from django.db.models import Sum

from people.models import Tutor, UserDepartmentSettings, User

from base.admin import CoursResource, DispoResource, VersionResource, \
    CoursPlaceResource, UnavailableRoomsResource, TutorCoursesResource, \
    CoursePreferenceResource, MultiDepartmentTutorResource, \
    SharedRoomGroupsResource
from displayweb.admin import BreakingNewsResource
from base.forms import ContactForm, PerfectDayForm
from base.models import Course, UserPreference, ScheduledCourse, EdtVersion, \
    CourseModification, Slot, Day, Time, RoomGroup, PlanningModification, \
    Regen, RoomPreference, Department, TimeGeneralSettings, CoursePreference, \
    TrainingProgramme, CourseType
import base.queries as queries
from base.weeks import *
from displayweb.models import BreakingNews

logger = logging.getLogger(__name__)

from django.db.models import Q

# <editor-fold desc="FAVICON">
# ----------
# FAVICON
# ----------


fav_regexp = r'^(?P<fav>(favicon.ico)|(site\.webmanifest)' \
             r'|(browserconfig\.xml)|(safari-pinned-tab.svg)' \
             r'|(mstile.*\.png)|(favicon.*\.png)|(android-chrome.*\.png)' \
             r'|(apple-touch-icon.*\.png))$'


def favicon(req, fav, **kwargs):
    return RedirectView.as_view(
        url=staticfiles_storage.url('base/img/favicons/' + fav),
        permanent=False)(req)


# </editor-fold desc="FAVICON">


# <editor-fold desc="VIEWERS">
# ----------
# VIEWERS
# ----------
def index(req):
    """
    Display department selection view.
    
    The view create a default department if not exist and 
    redirects to edt vue if only one department exist
    """
    def redirect_to_edt(department):
        reverse_url = reverse('base:edt', kwargs={'department': department.abbrev})
        #reverse_url = reverse('base:edt', department=department.abbrev)
        return reverse_url

    departments = Department.objects.all()

    if not departments:        
        # Create first department
        department = queries.create_first_department()
        return redirect(redirect_to_edt(department))
    elif len(departments) == 1:
        return redirect(redirect_to_edt(departments[0]))
    else:
        return TemplateResponse(req, 'base/departments.html', {'departments': departments})

def edt(req, year=None, week=None, splash_id=0, **kwargs):

    week, year = clean_edt_view_params(week, year)
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

    if req.user.is_authenticated:
        name_usr = req.user.username
        try:
            rights_usr = req.user.rights
        except ObjectDoesNotExist:
            rights_usr = 0
    else:
        name_usr = ''
        rights_usr = 0

    return TemplateResponse(req, 'base/show-edt.html',
            {
                'all_weeks': week_list(),
                'week': week,
                'year': year,
                'promo': promo,
                'une_salle': une_salle,
                'copie': copie,
                'gp': gp,
                'name_usr': name_usr,
                'rights_usr': rights_usr,
                'splash_id': splash_id,
                'time_settings': queries.get_time_settings(req.department),
                'days': num_all_days(year, week, req.department),
                'has_department_perm': req.user.is_authenticated and req.user.has_department_perm(req.department),
                'dept': req.department.abbrev
            })


def edt_light(req, year=None, week=None, **kwargs):
    week, year = clean_edt_view_params(week, year)
    promo = clean_train_prog(req)

    if req.GET:
        svg_h = req.GET.get('svg_h', '640')
        svg_w = req.GET.get('svg_w', '1370')
        gp_s = req.GET.get('gp_s', '1')
        gp_w = req.GET.get('gp_w', '30')
        svg_top_m = req.GET.get('top_m', '40')

        svg_h = int(svg_h)
        svg_w = int(svg_w)
        gp_s = float(gp_s)
        gp_w = int(gp_w)
        svg_top_m = int(svg_top_m)

    else:
        svg_h = 1000
        svg_w = 2000
        gp_s = .5
        gp_w = 30
        svg_top_m = 40

    une_salle = "salle?"  # RoomGroup.objects.all()[0].name

    return TemplateResponse(req, 'base/show-edt-light.html',
                  {
                      'all_weeks': week_list(),
                      'week': week,
                      'year': year,
                      'promo': promo,
                      'une_salle': une_salle,
                      'copie': 0,
                      'gp': '',
                      'name_usr': '',
                      'rights_usr': 0,
                      'splash_id': 0,
                      'time_settings': queries.get_time_settings(req.department),
                      'days': num_all_days(year, week, req.department),
                      'has_department_perm': False,
                      'dept': req.department.abbrev,
                      'tv_svg_h': svg_h,
                      'tv_svg_w': svg_w,
                      'tv_gp_s': gp_s,
                      'tv_gp_w': gp_w,
                      'tv_svg_top_m': svg_top_m
                  })


@login_required
def preferences(req, **kwargs):
    if req.user.is_student:
        return redirect("people:student_preferences")
    elif req.user.is_tutor:
        return redirect("base:stype", department=req.department)
    else:
        return HttpResponse("Contacter un administrateur.")


@login_required
def stype(req, *args, **kwargs):
    err = ''
    if req.method == 'GET':
        return TemplateResponse(req,
                      'base/show-stype.html',
                      {'date_deb': current_week(),
                       'date_fin': current_week(),
                       'name_usr': req.user.username,
                       'usr_pref_hours': req.user.tutor.pref_hours_per_day,
                       'usr_max_hours': req.user.tutor.max_hours_per_day,
                       'err': err,
                       'current_year': current_year,
                       'time_settings': queries.get_time_settings(req.department),
                       'days': num_all_days(1, 1, req.department)
                      })
    elif req.method == 'POST':
        if 'apply' in list(req.POST.keys()):
            print(req.POST['se_deb'])
            date_deb = {'week': req.POST['se_deb'],
                        'year': req.POST['year_deb']}
            date_fin = {'week': req.POST['se_fin'],
                        'year': req.POST['year_fin']}
            if date_deb['year'] < date_fin['year'] or \
                    (date_deb['year'] == date_fin['year']
                     and date_deb['week'] <= date_fin['week']):
                print(req.POST['apply'])
            else:
                date_deb = current_week()
                date_fin = current_week()
                err = "Problème : seconde semaine avant la première"

        else:
            date_deb = current_week()
            date_fin = current_week()

            print(req.POST['save'])

        return TemplateResponse(req,
                      'base/show-stype.html',
                      {'date_deb': date_deb,
                       'date_fin': date_fin,
                       'name_usr': req.user.username,
                       'usr_pref_hours': req.user.tutor.pref_hours_per_day,
                       'usr_max_hours': req.user.tutor.max_hours_per_day,
                       'err': err,
                       'current_year': current_year,
                       'time_settings': queries.get_time_settings(req.department),
                       'days': num_all_days(1, 1, req.department)
                      })


def user_perfect_day_changes(req, *args, **kwargs):
    t = req.user.tutor
    print('salut', t, type(t))
    data = req.POST
    user_pref_hours = int(data['user_pref_hours'][0])
    user_max_hours = int(data['user_max_hours'][0])
    t.pref_hours_per_day = user_pref_hours
    t.max_hours_per_day = user_max_hours
    t.save()
    return redirect('base:stype', req.department)





def aide(req, **kwargs):
    return TemplateResponse(req, 'base/aide.html',
                {'has_department_perm': req.user.is_authenticated and req.user.has_department_perm(req.department)})


@login_required
def decale(req, **kwargs):
    if req.method != 'GET':
        return TemplateResponse(req, 'base/aide.html', {})

    week_init = req.GET.get('s', '-1')
    year_init = req.GET.get('a', '-1')
    department = req.department

    liste_profs = []

    for p in Tutor.objects \
                    .filter(departments=department) \
                    .order_by('username'):
        liste_profs.append(p.username)

    return TemplateResponse(req, 'base/show-decale.html',
                  {'all_weeks': week_list(),
                   'week_init': week_init,
                   'year_init': year_init,
                   'profs': liste_profs
                  })


# </editor-fold desc="VIEWERS">


# <editor-fold desc="FETCHERS">
# ----------
# FETCHERS
# ----------


def fetch_cours_pl(req, year, week, num_copy, **kwargs):
    logger.info(f'REQ: fetch sched courses: {req}')

    try:
        week = int(week)
        year = int(year)
        num_copy = int(num_copy)
        department = req.department
    except:
        return HttpResponse("KO")

    logger.info(f"D{department} W{week} Y{year} N{num_copy}")

    cache_key = get_key_course_pl(department.abbrev, year, week, num_copy)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    ok = False
    version = 0
    dataset = None
    while not ok:
        if num_copy == 0:
            version = queries.get_edt_version(department=department,
                    week=week,
                    year=year, create=True)
        
        dataset = CoursPlaceResource() \
            .export(queries.get_scheduled_courses(
                        department=department,                         
                        week=week,
                        year=year,
                        num_copy=num_copy)
            )
        ok = num_copy != 0 \
             or (version == queries \
                                .get_edt_version(
                                    department=department, 
                                    week=week, 
                                    year=year))

    if dataset is None:
        raise Http404("What are you trying to do?")

    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['week'] = week
    response['year'] = year
    response['days'] = str(num_all_days(year, week, req.department))
    response['num_copy'] = num_copy
    
    cached = cache.set(cache_key, response)
    return response


def fetch_cours_pp(req, week, year, num_copy, **kwargs):
    logger.info(f"REQ: unscheduled courses; {req}")

    try:
        week = int(week)
        year = int(year)
        num_copy = int(num_copy)
        department = req.department
    except ValueError:
        return HttpResponse("KO")

    logger.info(f"D{department} W{week} Y{year} N{num_copy}")

    cache_key = get_key_course_pp(department.abbrev, year, week, num_copy)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    dataset = CoursResource() \
        .export(Course
                .objects
                .filter(
                        module__train_prog__department=department,
                        week=week,
                        year=year)
                .exclude(pk__in=ScheduledCourse
                         .objects
                         .filter(
                             course__module__train_prog__department=department,
                             work_copy=num_copy)
                         .values('course'))
                .select_related('group__train_prog',
                                'tutor',
                                'module',
                                'type',
                                'group',
                                'room_type',
                                'module__display'
                                ))

    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['week'] = week
    response['year'] = year

    cache.set(cache_key, response)
    return response


#@login_required
def fetch_dispos(req, year, week, **kwargs):
    logger.info(f"REQ: fetch dispos; {req}")
    if not req.user.is_authenticated:
        return HttpResponse("Pas connecte", status=401)

    try:
        week = int(week)
        year = int(year)
        department = req.department
    except ValueError:
        return HttpResponse("KO")

    cache_key = get_key_preferences_tutor(department.abbrev, year, week)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    busy_inst = Course.objects.filter(week=week,
                                      year=year,
                                      module__train_prog__department=department) \
        .distinct('tutor') \
        .values_list('tutor')
    
    busy_inst = list(chain(busy_inst, [req.user]))

    week_avail = UserPreference.objects \
        .filter(week=week,
                year=year,
                user__in=busy_inst) \
        .select_related('user')

    default_avail = UserPreference.objects \
        .exclude(user__in \
                     =week_avail \
                 .distinct('user') \
                 .values_list('user')) \
        .filter(week=None,
                user__in=busy_inst) \
        .select_related('user')

    dataset = DispoResource() \
        .export(list(chain(week_avail,
                           default_avail)))  # all())#
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    response['week'] = week
    response['year'] = year

    cache.set(cache_key, response)
    return response


def fetch_course_default_week(req, train_prog, course_type, **kwargs):
    '''
    Export course preferences of department req.department
    for week week, year year
    '''
    logger.info(f"REQ: fetch course preferences; {req}")

    tp = None
    ct = None
    try:
        tp = TrainingProgramme.objects.get(abbrev=train_prog, department=req.department)
        ct = CourseType.objects.get(name=course_type, department=req.department)
    except ObjectDoesNotExist:
        response = HttpResponse(content_type='text/csv')
        response['status'] = 'KO'
        if tp is None:
            response['more'] = 'No such training programme'
        else:
            response['more'] = 'No such course type'
        return response
            
    dataset = CoursePreferenceResource() \
        .export(CoursePreference.objects \
                .filter(week=None,
                        course_type=ct,
                        train_prog=tp
                ))

    response = HttpResponse(dataset.csv,
                            content_type='text/csv')

    response['department'] = req.department.abbrev
    response['training_programme'] = train_prog
    response['course_type'] = course_type
    response['status'] = 'OK'

    return response


def fetch_unavailable_rooms(req, year, week, **kwargs):
    logger.info(req)

    try:
        week = int(week)
        year = int(year)
        department = req.department
    except ValueError:
        return HttpResponse("KO")

    # ----------------
    # To be done later
    # ----------------
    #
    # cache_key = get_key_unavailable_rooms(department.abbrev, year, week)
    # cached = cache.get(cache_key)
    # if cached is not None:
    #     return cached

    # dataset = DispoResource() \
    #     .export(RoomPreference.objects.filter(
    #                                         room__departments = department, 
    #                                         semaine=week,
    #                                         an=year,
    #                                         value=0))
    # response = HttpResponse(dataset.csv,
    #                         content_type='text/csv')
    # cache.set(cache_key, response)


    response = HttpResponse(content_type='text/csv')
    response['week'] = week
    response['year'] = year

    return response
   

def fetch_all_tutors(req, **kwargs):
    '''
    Cache and return all tutors who teach in req.department
    '''
    logger.info(f'Get tutors D{req.department.abbrev}')
    cache_key = get_key_all_tutors(req.department.abbrev)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    tutor_list = [t.user.username \
                  for t in UserDepartmentSettings.objects\
                  .filter(department=req.department,
                          user__is_tutor=True)]
    response = JsonResponse(tutor_list, safe=False)
    cache.set(cache_key, response)
    return response


def fetch_user_default_week(req, username, **kwargs):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return HttpResponse('Problem')

    dataset = DispoResource() \
        .export(UserPreference.objects \
                .filter(week=None,
                        user=user))  # all())#
    response = HttpResponse(dataset.csv, content_type='text/csv')
    return response


def fetch_decale(req, **kwargs):
    if not req.is_ajax() or req.method != "GET":
        return HttpResponse("KO")

    week = int(req.GET.get('s', '0'))
    year = int(req.GET.get('a', '0'))
    module = req.GET.get('m', '')
    prof = req.GET.get('p', '')
    group = req.GET.get('g', '')
    department = req.department

    courses = []
    modules = []
    tutors = []
    module_tutors = []
    groups = []

    if year > 0 and week > 0:
        days = num_all_days(year, week, req.department)
    else:
        days = []

    course = filt_p(filt_g(filt_m(filt_sa(department, week, year), module), group), prof)

    for c in course:
        try:
            cp = ScheduledCourse.objects.get(course=c,
                                             work_copy=0)
            day = cp.day
            time = cp.start_time
        except ObjectDoesNotExist:
            day = ''
            time = -1
        if c.tutor is not None:
            courses.append({'i': c.id,
                            'm': c.module.abbrev,
                            'p': c.tutor.username,
                            'g': c.group.name,
                            'd': day,
                            't': time})

    course = filt_p(filt_g(filt_sa(department, week, year), group), prof) \
        .order_by('module__abbrev') \
        .distinct('module__abbrev')
    for c in course:
        modules.append(c.module.abbrev)

    course = filt_g(filt_sa(department, week, year), group) \
        .order_by('tutor__username') \
        .distinct('tutor__username')
    for c in course:
        if c.tutor is not None:
            tutors.append(c.tutor.username)

    if module != '':
        course_queryset = Course.objects.filter(module__train_prog__department=department)        
        course = filt_m(course_queryset, module) \
            .order_by('tutor__username') \
            .distinct('tutor__username')
        for c in course:
            if c.tutor is not None:
                module_tutors.append(c.tutor.username)

    course = filt_p(filt_m(filt_sa(department, week, year), module), prof) \
        .distinct('group')
    for c in course:
        groups.append(c.group.name)

    return JsonResponse({'cours': courses,
                         'modules': modules,
                         'profs': tutors,
                         'profs_module': module_tutors,
                         'groups': groups,
                         'jours': days})


def fetch_bknews(req, year, week, **kwargs):
    dataset = BreakingNewsResource() \
        .export(BreakingNews.objects.filter(
                                        department=req.department,
                                        year=year,
                                        week=week))
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    response['week'] = week
    response['year'] = year
    return response


def fetch_all_versions(req, **kwargs):
    """
    Export all EdtVersions in json
    """
    dataset = VersionResource() \
        .export(EdtVersion.objects.filter(department=req.department))
    response = HttpResponse(dataset.json,
                            content_type='text/json')
    return response


def fetch_week_infos(req, year, week, **kwargs):
    """
    Export aggregated infos of a given week:
    version number, required number of available slots,
    proposed number of available slots
    (not cached)
    """
    version = 0
    for dept in Department.objects.all():
        version += queries.get_edt_version(dept, week, year, create=True)

    proposed_pref, required_pref = \
        pref_requirements(req.user, year, week) if req.user.is_authenticated \
        else (-1, -1)

    try:
        regen = str(Regen.objects.get(department=req.department, week=week, year=year))
    except ObjectDoesNotExist:
        regen = 'I'
        
    response = JsonResponse({'version': version,
                             'proposed_pref': proposed_pref,
                             'required_pref': required_pref,
                             'regen':regen})
    return response


def pref_requirements(tutor, year, week):
    """
    Return a pair (filled, required): number of preferences
    that have been proposed VS required number of prefs, according
    to local policy
    """
    nb_courses = Course.objects.filter(tutor=tutor,
                                       week=week,
                                       year=year) \
                               .count()
    week_av = UserPreference \
        .objects \
        .filter(user=tutor,
                week=week,
                year=year)
    if not week_av.exists():
        filled = UserPreference \
            .objects \
            .filter(user=tutor,
                    week=None,
                    value__gte=1) \
            .count()
    else:
        filled = week_av \
            .filter(value__gte=1) \
            .count()
    return filled, 2*nb_courses



@cache_page(15 * 60)
def fetch_groups(req, **kwargs):
    """
    Return groups tree for a given department
    """
    groups = queries.get_groups(req.department.abbrev)
    return JsonResponse(groups, safe=False)

#@cache_page(15 * 60)
def fetch_rooms(req, **kwargs):
    """
    Return rooms for a given department
    """
    rooms = queries.get_rooms(req.department.abbrev)
    return JsonResponse(rooms, safe=False)    

def fetch_constraints(req, **kwargs):
    """
    Return course type constraints for a given department
    """
    constraints = queries.get_coursetype_constraints(req.department.abbrev)
    return JsonResponse(constraints, safe=False)    

def fetch_departments(req, **kwargs):
    """
    Return departments
    """
    depts = queries.get_departments()
    return JsonResponse(depts, safe=False)    


def fetch_course_types(req, **kwargs):
    """
    Return course types
    """
    course_types = queries.get_course_types(req.department)
    return JsonResponse(course_types, safe=False)    

def fetch_training_programmes(req, **kwargs):
    """
    Return training programmes
    """
    programmes = queries.get_training_programmes(req.department)
    return JsonResponse(programmes, safe=False)    


def fetch_tutor_courses(req, year, week, tutor, **kwargs):
    """
    Return all courses of tutor
    """
    logger.info(f"W{week} Y{year}")
    logger.info(f"Fetch {tutor} courses")
    dataset = TutorCoursesResource() \
        .export(ScheduledCourse.objects \
                    .filter(
                        course__week=week,
                        course__year=year,
                        work_copy=0,
                        course__tutor__username=tutor))
    return HttpResponse(dataset.csv, content_type='text/csv')


def fetch_extra_sched(req, year, week, **kwargs):
    """
    Return the unavailability periods due to teaching in other departments
    """
    tutors = []
    for scheduled in ScheduledCourse.objects.filter(
            course__week=week,
            course__year=year,
            work_copy=0,
            course__room_type__department=req.department).distinct('course__tutor'):
        tutor = scheduled.course.tutor
        if UserDepartmentSettings.objects.filter(user=tutor).count() > 1:
            tutors.append(tutor)

    dataset = MultiDepartmentTutorResource() \
        .export(ScheduledCourse.objects \
                .filter(
                    course__week=week,
                    course__year=year,
                    work_copy=0,
                    course__tutor__in=tutors,
                )
                .exclude(course__room_type__department=req.department))
    return HttpResponse(dataset.csv, content_type='text/csv')


def fetch_shared_roomgroups(req, year, week, **kwargs):
    # which room groups are shared among departments
    shared_roomgroups = []
    for rg in RoomGroup.objects.all(): 
        depts = set() 
        for rt in rg.types.all(): 
            depts.add(rt.department) 
            if len(depts) > 1: 
                shared_roomgroups.append(rg)

    # courses in any shared room
    courses = ScheduledCourse.objects \
                .filter(
                    course__week=week,
                    course__year=year,
                    work_copy=0,
                    room__in=shared_roomgroups,
                ) \
                .exclude(course__room_type__department=req.department)
    dataset = SharedRoomGroupsResource().export(courses)
    return HttpResponse(dataset.csv, content_type='text/csv')

# </editor-fold desc="FETCHERS">

# <editor-fold desc="CHANGERS">
# ----------
# CHANGERS
# ----------


@login_required
def edt_changes(req, **kwargs):
    bad_response = {'status':'KO', 'more':''}
    good_response = {'status':'OK', 'more':''}

    if not (req.user.is_tutor and req.user.is_staff):
        bad_response['more'] = "Pas membre de l'équipe encadrante"
        return JsonResponse(bad_response)
        

    impacted_inst = set()

    msg = 'Notation : (numero_week, numer_year, ' \
          + 'numero_jour, numero_creneau, prof)\n\n'

    if not req.is_ajax():
        bad_response['more'] = "Non ajax"
        return JsonResponse(bad_response)

    if req.method != "POST":
        bad_response['more'] = "Non POST"
        return bad_response


    try:
        week = req.GET.get('s', '')
        year = req.GET.get('a', '')
        work_copy = req.GET.get('c', '')
        week = int(week)
        year = int(year)
        work_copy = int(work_copy)
        version = None
        department = req.department
    except:
        bad_response['more'] \
            = "Problème semaine, année ou work_copy."
        return JsonResponse(bad_response)


    logger.info(f"REQ: edt change; {req.body}")
    logger.info(req.POST)

    old_version = json.loads(req.POST.get('v',-1))
    recv_changes = json.loads(req.POST.get('tab',[]))

    
    version = EdtVersion.objects.filter(week=week,
                                        year=year).aggregate(Sum('version'))['version__sum']

    logger.info(f'Versions: incoming {old_version}, currently {version}')

    if work_copy != 0 or old_version == version:
        with transaction.atomic():
            if work_copy == 0:
                edt_version = EdtVersion \
                    .objects \
                    .select_for_update() \
                    .get(department=department, week=week, year=year)
            for a in recv_changes:
                non_place = False
                co = Course.objects.get(id=a['id'])
                try:
                    cp = ScheduledCourse.objects.get(course=co,
                                                     work_copy=work_copy)
                except ObjectDoesNotExist:
                    non_place = True
                    cp = ScheduledCourse(course=co,
                                         work_copy=work_copy)

                m = CourseModification(course=co,
                                       version_old=old_version,
                                       initiator=req.user.tutor)
                # old_day = a.day.o
                # old_slot = a.slot.o
                new_day = a['day']['n']
                old_day = a['day']['o']
                new_start_time = a['start']['n']
                old_start_time = a['start']['o']
                old_room = a['room']['o']
                new_room = a['room']['n']
                new_week = a['week']['n']
                old_week = a['week']['o']
                new_year = a['year']['n']
                old_year = a['year']['o']
                new_tutor = a['tutor']['n']
                old_tutor = a['tutor']['o']

                if non_place:
                    # old_day = new_day
                    # old_slot = new_slot
                    if new_room is None:
                        new_room = old_room

                if new_day is not None:
                    # None, None means no change
                    # same, same means not scheduled before
                    if non_place:
                        cp.day = new_day
                        cp.start_time = new_start_time
                    m.day_old = cp.day
                    m.start_time_old = cp.start_time
                    cp.day = new_day
                    cp.start_time = new_start_time
                    logger.info(f"Course modification: {m}")
                    logger.info(f"New scheduled course: {cp}")
                if new_room is not None:
                    try:
                        sal_n = RoomGroup.objects.get(name=new_room)
                    except ObjectDoesNotExist:
                        if new_room == 'salle?':
                            bad_response['more'] \
                                = 'Oublié de trouver une salle ' \
                                  'pour un cours ?'
                        else:
                            bad_response['more'] = \
                                f"Problème : salle {new_room} inconnue"
                        return JsonResponse(bad_response)

                    if non_place:
                        cp.room = sal_n
                    m.room_old = cp.room
                    cp.room = sal_n
                if new_week is not None:
                    m.old_week = old_week
                    m.old_year = old_year
                    cp.course.week = new_week
                    cp.course.year = new_year
                cp.save()
                if work_copy == 0:
                    m.save()

                if new_tutor is not None:
                    try:
                        prev_tut = co.tutor
                        co.tutor = Tutor.objects.get(username=new_tutor)
                        co.save()
                        pm = PlanningModification(course=co,
                                                  old_week=co.week,
                                                  old_year=co.year,
                                                  tutor_old=prev_tut,
                                                  initiator=req.user.tutor)
                        pm.save()
                    except ObjectDoesNotExist:
                        bad_response['more'] = \
                            f"Problème : prof {new_tutor} inconnu"
                        return JsonResponse(bad_response)

                if new_week is not None or new_year is not None \
                   or new_day is not None or new_start_time is not None \
                   or new_tutor is not None:
                    msg += str(co) + '\n'
                    impacted_inst.add(co.tutor.username)
                    if new_tutor is not None:
                        impacted_inst.add(old_tutor)

                    msg += f'({old_week}, {old_year}, ' \
                           + f'{old_day}, {old_start_time}, {old_tutor})'
                    msg += ' -> ('
                    msg += str(new_week) if new_week is not None else '-'
                    msg += ', '
                    msg += str(new_year) if new_year is not None else '-'
                    msg += ', '
                    msg += str(new_day) if new_day is not None else '-'
                    msg += ', '
                    msg += str(new_start_time) if new_start_time is not None else '-'
                    msg += ','
                    msg += str(new_tutor) if new_tutor is not None else '-'
                    msg += ')\n\n'

            if work_copy == 0:
                edt_version.version += 1
                edt_version.save()

            if new_week is not None and new_year is not None:
                cache.delete(get_key_course_pl(department.abbrev, new_year, new_week, work_copy))
            cache.delete(get_key_course_pl(department.abbrev, old_year, old_week, work_copy))
            cache.delete(get_key_course_pp(department.abbrev, old_year, old_week, work_copy))
            

        # subject = '[Modif sur tierce] ' + req.user.username \
        #           + ' a déplacé '
        # for inst in impacted_inst:
        #     if inst is not req.user.username:
        #         subject += inst + ' '

        # if len(impacted_inst) > 0 and work_copy == 0:
        #     if len(impacted_inst) > 1 \
        #             or req.user.username not in impacted_inst:
        #         send_mail(
        #             subject,
        #             msg,
        #             'edt@iut-blagnac',
        #             ['edt.info.iut.blagnac@gmail.com']
        #         )
        logger.info('Envoi de mail')
        logger.info(msg)
        

        return JsonResponse(good_response)
    else:
        bad_response['more'] = f"Version: {version} VS {old_version}"
        return JsonResponse(bad_response)



class HelperUserPreference():
    def __init__(self, tutor):
        self.tutor = tutor

    def filter(self):
        return UserPreference.objects.filter(user=self.tutor)

    def generate(self, week, year, day, start_time, duration, value):
        return UserPreference(user=self.tutor,
                              week=week,
                              year=year,
                              day=day,
                              start_time=start_time,
                              duration=duration,
                              value=value)


class HelperCoursePreference():
    def __init__(self, training_programme, course_type):
        self.training_programme = training_programme
        self.course_type = course_type

    def filter(self):
        return CoursePreference.objects.filter(train_prog=self.training_programme,
                                               course_type=self.course_type)

    def generate(self, week, year, day, start_time, duration, value):
        return CoursePreference(train_prog=self.training_programme,
                                course_type=self.course_type,
                                week=week,
                                year=year,
                                day=day,
                                start_time=start_time,
                                duration=duration,
                                value=value)
        

def preferences_changes(req, year, week, helper_pref):
    good_response = {'status':'OK', 'more':''}

    # if no preference was present for this week, first copy the
    # default availabilities

    changes = json.loads(req.POST.get('changes','{}'))
    logger.info("List of changes")
    for a in changes:
        logger.info(a)
    
    # Default week at None
    if week == 0 or year == 0:
        week = None
        year = None

    if not helper_pref.filter().filter(
            week=week,
            year=year).exists():
        for pref in helper_pref.filter().filter(week=None):
            new_dispo = helper_pref.generate(week,
                                             year,
                                             pref.day,
                                             pref.start_time,
                                             pref.duration,
                                             pref.value)
            logger.info(new_dispo)
            new_dispo.save()

    for a in changes:
        logger.info(f"Change {a}")
        helper_pref.filter().filter(week=week,
                                    year=year,
                                    day=a['day']).delete()
        for pref in a['val_inter']:
            new_dispo = helper_pref.generate(week,
                                             year,
                                             a['day'],
                                             pref['start_time'],
                                             pref['duration'],
                                             pref['value'])
            logger.info(new_dispo)
            new_dispo.save()

    logger.info('Pref changed with success')
    return JsonResponse(good_response)


def check_ajax_post(req):
    response = {'status':'KO', 'more':''}

    if not req.is_ajax():
        response['more'] = "Non ajax"
        return JsonResponse(response)

    if req.method != "POST":
        response['more'] = "Non POST"
        return JsonResponse(response)

    return None



    
@login_required
def user_preferences_changes(req, year, week, username, **kwargs):
    response = check_ajax_post(req)
    if response is not None:
        return response

    response = {'status':'KO', 'more':''}
    
    usr_change = username

    logger.info(f"REQ: dispo change for {usr_change} by {req.user.username}")
    logger.info(f"     W{week} Y{year}")
    
    tutor = None
    try:
        tutor = Tutor.objects.get(username=usr_change)
    except ObjectDoesNotExist:
        response['more'] \
            = "Problème d'utilisateur."
        return JsonResponse(response)

    if tutor.username != req.user.username and req.user.rights >> 1 % 2 == 0:
        response['more'] \
            = 'Non autorisé, réclamez plus de droits.'
        return JsonResponse(response)

    # print(q)
    response = preferences_changes(req, year, week, HelperUserPreference(tutor))

    if week is not None and year is not None:
        # invalidate merely the keys where the tutor has courses:
        # bad idea if the courses have not been generated yet
        # for c in Course.objects.filter(semaine=week,
        #                               an=year).distinct('module__train_prog__department'):
        for dep in Department.objects.all():
            cache.delete(get_key_preferences_tutor(dep.abbrev, year, week))

    return response

        



def course_preferences_changes(req, year, week, train_prog, course_type, **kwargs):
    response = check_ajax_post(req)
    logger.info(response)
    if response is not None:
        return response

    response = {'status':'KO', 'more':''}
    
    tp = None
    ct = None
    try:
        tp = TrainingProgramme.objects.get(abbrev=train_prog, department=req.department)
        ct = CourseType.objects.get(name=course_type, department=req.department)
    except ObjectDoesNotExist:
        if tp is None:
            response['more'] = 'No such training programme'
        else:
            response['more'] = 'No such course type'
        return JsonResponse(response)

    return preferences_changes(req, year, week, HelperCoursePreference(tp, ct))



@login_required
def decale_changes(req, **kwargs):
    bad_response = HttpResponse("KO")
    good_response = HttpResponse("OK")
    print(req)

    if not req.is_ajax():
        bad_response['reason'] = "Non ajax"
        return bad_response

    if req.method != "POST":
        bad_response['reason'] = "Non POST"
        return bad_response

    new_assignment = json.loads(req.POST.get('new',{}))
    change_list = json.loads(req.POST.get('liste',[]))
    new_week = new_assignment['ns']
    new_year = new_assignment['na']

    for c in change_list:
        changing_course = Course.objects.get(id=c['i'])
        old_week = changing_course.week
        old_year = changing_course.year

        edt_versions = EdtVersion.objects.select_for_update().filter(
            (Q(week=old_week) & Q(year=old_year))
             |(Q(week=new_week) & Q(year=new_year)), department=req.department)
        
        with transaction.atomic():
            # was the course was scheduled before?
            if c['d'] != '' and c['t'] != -1:
                scheduled_course = ScheduledCourse \
                    .objects \
                    .get(course=changing_course,
                         work_copy=0)
                cache.delete(get_key_course_pl(req.department.abbrev,
                                               old_year,
                                               old_week,
                                               scheduled_course.work_copy))
                scheduled_course.delete()
                ev = EdtVersion.objects.get(year=old_year, week=old_week, department=req.department)
                ev.version += 1
                ev.save()
            else:
                cache.delete(get_key_course_pp(req.department.abbrev, 
                                               old_year,
                                               old_week,
                                               0))
                # note: add work_copy in Cours might be of interest

            pm = PlanningModification(course=changing_course,
                                      old_week=old_week,
                                      old_year=old_year,
                                      tutor_old=changing_course.tutor,
                                      initiator=req.user.tutor)
            pm.save()

            changing_course.week = new_week
            changing_course.year = new_year
            if new_year != 0:
                changing_course.tutor = Tutor.objects.get(username=new_assignment['np'])
            cache.delete(get_key_course_pp(req.department.abbrev,
                                           new_year,
                                           new_week,
                                           0))
            changing_course.save()
            ev, _ = EdtVersion.objects.update_or_create(
                year=new_year,
                week=new_week, 
                department=req.department)
            ev.version += 1
            ev.save()

    return good_response


# </editor-fold desc="CHANGERS">

# <editor-fold desc="EMAILS">
# ---------
# E-MAILS
# ---------


def contact(req, **kwargs):
    ack = ''
    if req.method == 'POST':
        form = ContactForm(req.POST)
        if form.is_valid():
            dat = form.cleaned_data
            recip_send = [Tutor.objects.get(username=
                                            dat.get("recipient")).email,
                          dat.get("sender")]
            try:
                email = EmailMessage(
                    '[EdT IUT Blagnac] ' + dat.get("subject"),
                    "(Cet e-mail vous a été envoyé depuis le site des emplois"
                    " du temps de l'IUT de Blagnac)\n\n"
                    + dat.get("message"),
                    to=recip_send,
                    reply_to=[dat.get("sender")]
                )
                email.send()
            except:
                ack = 'Envoi du mail impossible !'
                return TemplateResponse(req, 'base/contact.html',
                              {'form': form,
                               'ack': ack
                              })

            return edt(req, None, None, 1)
    else:
        init_mail = ''
        if req.user.is_authenticated:
            init_mail = req.user.email
        form = ContactForm(initial={
            'sender': init_mail})
    return TemplateResponse(req, 'base/contact.html',
                  {'form': form,
                   'ack': ack
                  })


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


def clean_edt_view_params(week, year):

    if week is None or year is None:
        today = current_week()
        week = today['week']
        year = today['year']
    else:
        try:
            week = int(week)
            year = int(year)
        except ValueError:
            today = current_week()
            week = today['week']
            year = today['year']

    return week, year


def filt_m(r, module):
    if module != '':
        r = r.filter(module__abbrev=module)
    return r


def filt_p(r, prof):
    if prof != '':
        r = r.filter(tutor__username=prof)
    return r


def filt_g(r, group):
    if group != '':
        r = r.filter(group__name=group)
    return r


def filt_sa(department, week, year):
    return Course.objects.filter(module__train_prog__department=department,
                                 week=week,
                                 year=year)


def get_key_course_pl(department_abbrev, year, week, num_copy):
    if year is None or week is None or num_copy is None:
        return ''
    return f'CPL-D{department_abbrev}-Y{year}-W{week}-C{num_copy}'


def get_key_course_pp(department_abbrev, year, week, num_copy):
    if year is None or week is None or num_copy is None:
        return ''
    return f'CPP-D{department_abbrev}-Y{year}-W{week}-C{num_copy}'


def get_key_preferences_tutor(department_abbrev, year, week):
    if year is None or week is None:
        return ''
    return f'PREFT-D{department_abbrev}-Y{year}-W{week}'


def get_key_unavailable_rooms(department_abbrev, year, week):
    if year is None or week is None:
        return ''
    return f'UNAVR-D{department_abbrev}-Y{year}-W{week}'


def get_key_all_tutors(department_abbrev):
    return f'ALL-TUT-D{department_abbrev}'

# </editor-fold desc="HELPERS">



