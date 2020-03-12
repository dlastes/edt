from django.shortcuts import render
from django.template import loader
from django.template.loader import get_template
from django.http import HttpResponse
from base.models import ScheduledCourse, Group, Room
import base.queries as queries
from people.models import Tutor
from datetime import datetime
from datetime import timedelta
#from base.weeks import get_course_datetime_start
from isoweek import Week
from django.core.cache import cache

tz='Europe/Paris'


def index(request, **kwargs):
    enseignant_list = Tutor.objects.filter(is_active=True, is_tutor=True).order_by('username')
    group_list = Group.objects.filter(basic=True,
                                       train_prog__department=request.department)\
                               .order_by('train_prog__abbrev', 'name')
    salle_list = queries.get_rooms(None, basic=True).order_by('name')
    context = { 'enseignants': enseignant_list, 'groupes':group_list, 'salles':salle_list }
    return render(request, 'synchro/index.html', context=context)


def tutor(request, id, **kwargs):
    events=[]
    for c in get_course_list().filter(course__tutor__username=id):
        e = create_event(c)
        e['title'] = c.course.module.abbrev + ' ' + c.course.type.name + ' - ' + c.course.group.train_prog.abbrev + ' ' + c.course.group.name
        events.append(e)
    response = render(request, 'synchro/ical.ics', context={'events':events, 'timezone':tz}, content_type='text/calendar; charset=utf8')
    response['Content-Disposition'] = f'attachment; filename={id}.ics'
    return response


def group(request, promo_id, group_id, **kwargs):
    g = Group.objects.get(name=group_id, train_prog__abbrev=promo_id)
    g_list = g.ancestor_groups()
    g_list.add(g)
    events=[]
    for c in get_course_list().filter(course__group__in=g_list):
        e = create_event(c)
        tutor = c.course.tutor.username if c.course.tutor is not None else ''
        e['title'] = c.course.module.abbrev + ' ' + c.course.type.name + ' - ' + tutor
        events.append(e)
    response = render(request, 'synchro/ical.ics', context={'events':events, 'timezone':tz}, content_type='text/calendar; charset=utf8')
    response['Content-Disposition'] = f'attachment; filename={promo_id}{group_id}.ics'
    return response


def room(request, id, **kwargs):
    events=[]
    for c in  get_course_list().filter(room__name=id):
        e = create_event(c)
        events.append(e)
    response = render(request, 'synchro/ical.ics', context={'events':events, 'timezone':tz}, content_type='text/calendar; charset=utf8')
    response['Content-Disposition'] = f'attachment; filename={id}.ics'
    return response


def get_course_list():
    return ScheduledCourse.objects.filter(work_copy=0).order_by('course__year', 'course__week', 'slot__day_id', 'slot__hour')


def create_event(c):
    begin = datetime.combine(Week(c.course.year, c.course.week).day(c.slot.day_id-1),
                             datetime.min.time()) \
                             + timedelta(hours=c.slot.hour.hours,
                                         minutes=c.slot.hour.minutes)
    end = begin + timedelta(minutes=c.slot.duration)
    tutor = c.course.tutor.username if c.course.tutor is not None else ''
    location = c.room.name if c.room is not None else ''
    return {'id':c.id,
         'title': c.course.module.abbrev + ' ' + c.course.type.name + ' - ' + c.course.group.train_prog.abbrev + ' ' + c.course.group.name + ' - ' + tutor,
         'location': location,
         'begin': begin,
         'end': end,
         'description': 'Cours \: ' + c.course.module.abbrev + ' ' + c.course.type.name +'\\n'+
           'Groupe \: ' + c.course.group.train_prog.abbrev + ' ' + c.course.group.name +'\\n'+
           'Enseignant : ' + c.course.tutor.username +'\\n' +
           'Salle \: ' + location
    }
