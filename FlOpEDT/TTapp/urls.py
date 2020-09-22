from django.conf.urls import url, include
from django.urls import path

import TTapp.views

app_name="TTapp"

urlpatterns = [
    path('side_panel/<int:year>/<int:week>',
         TTapp.views.available_work_copies,
         name="available_work_copies"),
    path('check_swap/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.check_swap,
         name="check_swap"),
    path('swap/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.swap,
         name="swap"),
    path('reassign_rooms/<int:year>/<int:week>/<int:work_copy>',
         TTapp.views.reassign_rooms,
         name="reassign_rooms"),
    path('fetch_group_lunch',
         TTapp.views.fetch_group_lunch,
         name="fetch_group_lunch"),
]
