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
        course = scourse.course
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.group.train_prog.abbrev} G{course.group.name}'
        )

    def item_description(self, scourse):
        location = scourse.room.name if scourse.room is not None else ''
        course = scourse.course
        tutor = scourse.tutor
        return (f'Cours : {course.module.abbrev} {course.type.name}\n'
                f'Groupe : {course.group.train_prog.abbrev} '
                f'{course.group.name}\n'
                f'Enseignant : {tutor}\nSalle : {location}'
        )

    def item_start_datetime(self, scourse):
        course = scourse.course
        begin = datetime.combine(
            Week(course.year, course.week)\
            .day(self.days.index(scourse.day)),
            datetime.min.time()) \
            + timedelta(minutes=scourse.start_time)
        return begin

    def item_end_datetime(self, scourse):
        end = self.item_start_datetime(scourse) \
            + timedelta(minutes=scourse.course.type.duration)
        return end

    def item_link(self, s):
        return str(s.id)


class TutorEventFeed(EventFeed):
    def get_object(self, request, department, tutor_id):
        return Tutor.objects.get(id=tutor_id)

    def items(self, tutor):
        return ScheduledCourse.objects.filter(tutor=tutor, work_copy=0)\
                                      .order_by('-course__year','-course__week')

    def item_title(self, scourse):
        course = scourse.course
        location = scourse.room.name if scourse.room is not None else ''
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.group.train_prog.abbrev} G{course.group.name} '
                f'- {location}'
        )

class RoomEventFeed(EventFeed):
    def get_object(self, request, department, room_id):
        return Room.objects.get(id=room_id).and_subrooms()

    def items(self, room_groups):
        return ScheduledCourse.objects\
                              .filter(room__in=room_groups, work_copy=0)\
                              .order_by('-course__year','-course__week')

    def item_title(self, scourse):
        course = scourse.course
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {course.group.train_prog.abbrev} G{course.group.name}'
                f'- {scourse.tutor.username}'
        )


class GroupEventFeed(EventFeed):
    def get_object(self, request, department, group_id):
        gp = Group.objects.get(id=group_id)
        gp_included = gp.ancestor_groups()
        gp_included.add(gp)
        return gp_included

    def items(self, groups):
        return ScheduledCourse.objects\
                              .filter(course__group__in=groups, work_copy=0\
                              ).order_by('-course__year','-course__week')

    def item_title(self, scourse):
        course = scourse.course
        location = scourse.room.name if scourse.room is not None else ''
        return (f'{course.module.abbrev} {course.type.name} '
                f'- {scourse.tutor.username} '
                f'- {location}'
        )
