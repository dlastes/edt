from django.conf.urls import url, include

import TTapp.views

urlpatterns = [
    url('viewForm/<str:funcname>', TTapp.views.viewForm)
]