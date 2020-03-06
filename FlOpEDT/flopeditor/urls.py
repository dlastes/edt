# -*- coding: utf-8 -*-
"""
Python versions: Python 3.6

This file is part of the FlOpEDT/FlOpScheduler project.
Copyright (c) 2017
Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program. If not, see
<http://www.gnu.org/licenses/>.

You can be released from the requirements of the license by purchasing
a commercial license. Buying such a license is mandatory as soon as
you develop activities involving the FlOpEDT/FlOpScheduler software
without disclosing the source code of your own applications.


This module is used to declare the urls related to FlopEditor, an app used
to manage a department statistics for FlOpEDT.
"""

from django.urls import path
from . import views, crud

app_name = "flopeditor"

urlpatterns = [
    # directly reachable by users
    # ---------------------------
    path('', views.home, name='flopeditor-home'),
    path('<slug:department_abbrev>/', views.department_default,
         name='flopeditor-department-default'),
    path('<slug:department_abbrev>/rooms', views.department_rooms,
         name='flopeditor-department-rooms'),
    path('<slug:department_abbrev>/groups', views.department_groups,
         name='flopeditor-department-groups'),
    path('<slug:department_abbrev>/modules', views.department_modules,
         name='flopeditor-department-modules'),
    path('<slug:department_abbrev>/classes', views.department_classes,
         name='flopeditor-department-classes'),
    path('<slug:department_abbrev>/parameters', views.department_parameters,
         name='flopeditor-department-parameters'),
    path('<slug:department_abbrev>/parameters/edit', views.department_parameters_edit,
         name='flopeditor-department-parameters-edit'),

    # exchanges with the db via django
    # --------------------------------
    path('ajax/create-department', views.ajax_create_department,
         name="flopeditor-ajax-create-department"),
    path('ajax/parameters-edit/<slug:department_abbrev>', views.ajax_edit_parameters,
         name='flopeditor-ajax-edit-department-parameters'),

    # exchanges with the CRUD
    # --------------------------------
    path('<slug:department_abbrev>/crud/group_type', crud.crud_student_group_type,
        name='flopeditor-crud-student-group-type')

]
