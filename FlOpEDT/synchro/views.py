from django.shortcuts import render
from django.template import loader
from django.template.loader import get_template
from django.http import HttpResponse
from base.models import ScheduledCourse, Group, Room
from people.models import Tutor
from datetime import datetime
from datetime import timedelta

tz='Europe/Paris'


def index(request, **kwargs):
    enseignant_list = Tutor.objects.filter(is_active=True, is_tutor=True).order_by('username')
    groupe_list = Group.objects.filter(basic=True,
                                       train_prog__department=request.department)\
                               .order_by('train_prog__abbrev', 'nom')
    salle_list = Room.objects.order_by('name')
    context = { 'enseignants': enseignant_list, 'groupes':groupe_list, 'salles':salle_list }
    return render(request, 'synchro/index.html', context)


def tutor(request, id, **kwargs):
    events=[]
    for c in get_course_list().filter(cours__tutor__username=id):
        e = create_event(c)
        e['title'] = c.cours.module.abbrev + ' ' + c.cours.type.name + ' - ' + c.cours.groupe.train_prog.abbrev + ' ' + c.cours.groupe.nom
        events.append(e)
    return render(request, 'synchro/ical.ics', {'events':events, 'timezone':tz})


def group(request, promo_id, groupe_id, **kwargs):
    g = Group.objects.get(nom=groupe_id, train_prog__abbrev=promo_id)
    g_list = g.ancestor_groups()
    g_list.add(g)
    events=[]
    for c in get_course_list().filter(cours__groupe__in=g_list):
        e = create_event(c)
        e['title'] = c.cours.module.abbrev + ' ' + c.cours.type.name + ' - ' + c.cours.tutor.username
        events.append(e)
    return render(request, 'synchro/ical.ics', {'events':events, 'timezone':tz})


def room(request, id, **kwargs):
    events=[]
    for c in  get_course_list().filter(room__name=id):
        e = create_event(c)
        events.append(e)
    return render(request, 'synchro/ical.ics', {'events':events, 'timezone':tz})


def get_course_list():
    return ScheduledCourse.objects.filter(copie_travail=0).order_by('cours__an', 'cours__semaine', 'creneau__jour_id', 'creneau__heure')


def create_event(c):
    p = str(c.cours.an) + '-W' + str(c.cours.semaine) + '-w' + str(c.creneau.jour_id) + ' ' + str(c.creneau.heure.hours) + ':'+ str(c.creneau.heure.minutes)
    begin = datetime.strptime(p, '%Y-W%W-w%w %H:%M')
    end = begin + timedelta(minutes=c.creneau.duration)
    location = c.room.name if c.room is not None else ''
    return {'id':c.id,
         'title': c.cours.module.abbrev + ' ' + c.cours.type.name + ' - ' + c.cours.groupe.train_prog.abbrev + ' ' + c.cours.groupe.nom + ' - ' + c.cours.tutor.username,
         'location': location,
         'begin': begin,
         'end': end,
         'description': 'Cours \: ' + c.cours.module.abbrev + ' ' + c.cours.type.name +'\\n'+
           'Groupe \: ' + c.cours.groupe.train_prog.abbrev + ' ' + c.cours.groupe.nom +'\\n'+
           'Enseignant : ' + c.cours.tutor.username +'\\n' +
           'Salle \: ' + location
    }
