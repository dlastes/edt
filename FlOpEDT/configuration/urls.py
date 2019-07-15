from django.conf.urls import url
from . import views

app_name="configuration"

urlpatterns = [
    url(r'^$', views.configuration, name="configuration"),
    url(r'^import_config_file/$', views.import_config_file, name="import_config_file"),
    url(r'^import_planif_file/$', views.import_planif_file, name="import_planif_file"),
    url(r'^get_config_file/$', views.get_config_file, name="get_config_file"),
    url(r'^get_planif_file/$', views.get_planif_file, name="get_planif_file"),
]
