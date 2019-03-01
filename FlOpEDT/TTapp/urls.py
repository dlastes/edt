from django.conf.urls import url, include
from django.urls import path

import TTapp.views

urlpatterns = [
    path('viewForm/<str:funcname>', TTapp.views.viewForm)
]