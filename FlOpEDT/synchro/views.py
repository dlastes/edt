from django.shortcuts import render
from django.template import loader
from django.template.loader import get_template
from django.http import HttpResponse
from base.models import ScheduledCourse
from datetime import datetime
from datetime import timedelta

tz='Europe/Paris'


def index(request):
    enseignant_list = []#TODO is_active=True, is_tutor=True
    groupe_list = []#TODO basic=True
    salle_list = []#TODO
    context = { 'enseignants': enseignant_list, 'groupes':groupe_list, 'salles':salle_list }
    return render(request, 'index.html', context)


def enseignant(request, id):
    events=[]
    for c in get_course_list().filter(cours__tutor__username=id):
        e = create_event(c)
        e['title'] = c.cours.module.abbrev + ' ' + c.cours.type.name + ' - ' + c.cours.groupe.train_prog.abbrev + ' ' + c.cours.groupe.nom
        events.append(e)
    return render(request, 'ical.ics', {'events':events, 'timezone':tz})


def groupe(request, promo_id, groupe_id):
    events=[]
    for c in get_course_list().filter(cours__groupe__basic=True, cours__groupe__nom=groupe_id, cours__groupe__train_prog__abbrev=promo_id):
        e = create_event(c)
        e['title'] = c.cours.module.abbrev + ' ' + c.cours.type.name + ' - ' + c.cours.tutor.username
        events.append(e)
    return render(request, 'ical.ics', {'events':events, 'timezone':tz})


def salle(request, id):
    events=[]
    for c in  get_course_list().filter(room__name=id):
        e = create_event(c)
        events.append(e)
    return render(request, 'ical.ics', {'events':events, 'timezone':tz})


def get_course_list():
    return ScheduledCourse.objects.filter(copie_travail=0).order_by('cours__an', 'cours__semaine', 'creneau__jour_id', 'creneau__heure')


def create_event(c):
    p = str(c.cours.an) + '-W' + str(c.cours.semaine) + '-w' + str(c.creneau.jour_id) + ' ' + str(c.creneau.heure.hours) + ':'+ str(c.creneau.heure.minutes)
    begin = datetime.strptime(p, '%Y-W%W-w%w %H:%M')
    end = begin + timedelta(minutes=c.creneau.duration)
    return {'id':c.id,
         'title': c.cours.module.abbrev + ' ' + c.cours.type.name + ' - ' + c.cours.groupe.train_prog.abbrev + ' ' + c.cours.groupe.nom + ' - ' + c.cours.tutor.username,
         'location': c.room.name,
         'begin': begin,
         'end': end,
         'description': 'Cours \: ' + c.cours.module.abbrev + ' ' + c.cours.type.name +'\\n'+
           'Groupe \: ' + c.cours.groupe.train_prog.abbrev + ' ' + c.cours.groupe.nom +'\\n'+
           'Enseignant : ' + c.cours.tutor.username +'\\n' +
           'Salle \: ' + c.room.name
    }
