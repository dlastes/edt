from datetime import datetime
from datetime import timedelta
from isoweek import Week

from django_ical.views import ICalFeed

from base.models import ScheduledCourse
from people.models import Tutor


class EventFeed(ICalFeed):
    """
    A simple event calender
    """
    product_id = 'flop'
    timezone = 'Europe/Paris'

    def get_object(self, request, tutor_name):
        return Tutor.objects.get(username=tutor_name)

    def items(self, tutor):
        return ScheduledCourse.objects.filter(cours__tutor=tutor, copie_travail=0).order_by('-cours__an','-cours__semaine')

    def item_title(self, scourse):
        course = scourse.cours
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.groupe.train_prog.abbrev} {course.groupe.nom}'
        )

    def item_description(self, scourse):
        location = scourse.room.name if scourse.room is not None else ''
        course = scourse.cours
        tutor = course.tutor
        return (f'Cours : {course.module.abbrev} {course.type.name}\n'
                f'Groupe : {course.groupe.train_prog.abbrev} {course.groupe.nom}\n'
                f'Enseignant : {tutor}\nSalle : {location}'
        )

    def item_start_datetime(self, scourse):
        course = scourse.cours
        begin = datetime.combine(
            Week(course.an, course.semaine)\
            .day(scourse.creneau.jour_id-1),
            datetime.min.time()) \
            + timedelta(hours=scourse.creneau.heure.hours,
                        minutes=scourse.creneau.heure.minutes)
        return begin

    def item_end_datetime(self, scourse):
        end = self.item_start_datetime(scourse) + timedelta(minutes=scourse.creneau.duration)
        return end

    def item_link(self, s):
        return str(s.id)
