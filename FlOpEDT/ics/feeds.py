from datetime import datetime
from datetime import timedelta
from isoweek import Week

from django_ical.views import ICalFeed

from django.core.exceptions import ObjectDoesNotExist

from base.models import ScheduledCourse, Room, Group, Day
from people.models import Tutor


class EventFeed(ICalFeed):
    """
    A simple event calender
    """
    product_id = 'flop'
    timezone = 'Europe/Paris'
    days = [abbrev for abbrev,_ in Day.CHOICES]

    def item_title(self, scourse):
        course = scourse.cours
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.group.train_prog.abbrev} G{course.group.name}'
        )

    def item_description(self, scourse):
        location = scourse.room.name if scourse.room is not None else ''
        course = scourse.cours
        tutor = course.tutor
        return (f'Cours : {course.module.abbrev} {course.type.name}\n'
                f'Groupe : {course.group.train_prog.abbrev} {course.group.name}\n'
                f'Enseignant : {tutor}\nSalle : {location}'
        )

    def item_start_datetime(self, scourse):
        course = scourse.cours
        begin = datetime.combine(
            Week(course.an, course.semaine)\
            .day(self.days.index(scourse.day)),
            datetime.min.time()) \
            + timedelta(minutes=scourse.start_time)
        return begin

    def item_end_datetime(self, scourse):
        end = self.item_start_datetime(scourse) + timedelta(minutes=scourse.course.type.duration)
        return end

    def item_link(self, s):
        return str(s.id)


class TutorEventFeed(EventFeed):
    def get_object(self, request, department, tutor):
        return Tutor.objects.get(username=tutor)

    def items(self, tutor):
        return ScheduledCourse.objects.filter(course__tutor=tutor, work_copy=0).order_by('-course__an','-course__semaine')

    def item_title(self, scourse):
        course = scourse.cours
        location = scourse.room.name if scourse.room is not None else ''
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.group.train_prog.abbrev} G{course.group.name} '
                f'- {location}'
        )

class RoomEventFeed(EventFeed):
    def get_object(self, request, department, room):
        try:
            room_o = Room.objects.get(name=room)
        except ObjectDoesNotExist:
            try:
                room_o = Room.objects.get(name=room.replace('_',' '))
            except ObjectDoesNotExist:
                return []
        return room_o.subroom_of.all()

    def items(self, room_groups):
        return ScheduledCourse.objects.filter(room__in=room_groups, work_copy=0).order_by('-course__an','-course__semaine')

    def item_title(self, scourse):
        course = scourse.cours
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.group.train_prog.abbrev} G{course.group.name}'
                f'- {course.tutor.username}'
        )


class GroupEventFeed(EventFeed):
    def get_object(self, request, department, training_programme, group):
        print(department, training_programme, group)
        gp = Group.objects.get(name=group,
                               train_prog__abbrev=training_programme)
        gp_included = gp.ancestor_groups()
        gp_included.add(gp)
        return gp_included

    def items(self, groups):
        return ScheduledCourse.objects.filter(course__groupe__in=groups, work_copy=0).order_by('-course__an','-course__semaine')

    def item_title(self, scourse):
        course = scourse.cours
        location = scourse.room.name if scourse.room is not None else ''
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.tutor.username} '
                f'- {location}'
        )
