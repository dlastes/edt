from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index),
    url(r'enseignant/(?P<id>\w+)\.ics$', views.enseignant),
    url(r'salle/(?P<id>\w+)\.ics$', views.salle),
    url(r'groupe/(?P<promo_id>\w+)/(?P<groupe_id>\w+)\.ics$', views.groupe)
]
