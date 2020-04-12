from django.urls import path
from ics.feeds import TutorEventFeed, RoomEventFeed, GroupEventFeed

from ics import views

app_name = 'ics'

urlpatterns = [
    path(r'', views.index, name="index"),
    path(r'tutor/<int:tutor_id>.ics', TutorEventFeed(), name="tutor"),
    path(r'room/<int:room_id>.ics', RoomEventFeed(), name="room"),
    path(r'group/<int:group_id>.ics', GroupEventFeed(), name="group")
]
