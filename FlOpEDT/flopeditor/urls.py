"""
    Flopeditor URLs.
"""

from django.urls import path
from . import views

app_name="flopeditor"

urlpatterns = [
    path('', views.home, name='flopeditor-home'),
    path('<slug:department>/', views.department_parameters, name='flopeditor-department-default'),
]
