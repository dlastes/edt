from django.urls import path
from ics.feeds import EventFeed

app_name = 'ics'

urlpatterns = [
    path(r'<slug:tutor_name>.ics', EventFeed()),
]
