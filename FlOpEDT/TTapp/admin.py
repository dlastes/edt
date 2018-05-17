# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.


from __future__ import unicode_literals

from django.contrib import admin

from TTapp.models import LimitNaturePerPeriod, ReasonableDays, Stabilize, MinHalfDays, MinNonPreferedSlot, AvoidBothSlots, SimultaneousCourses



# Register your models here.

# from TTapp.models import TestJour

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, DropdownFilterCho



# class TestJourResource(resources.ModelResource):
#     id = fields.Field(column_name='id_jour',attribute='jour',widget=ForeignKeyWidget(Jour,'id'))

# class TestJourAdmin(admin.ModelAdmin):
#     list_display = ('jour','truc')

# admin.site.register(TestJour, TestJourAdmin)

class LimitNaturePerPeriodAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'nature', 'limit', 'promo',
                    'module', 'prof', 'period', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('promo', DropdownFilterAll),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('prof', DropdownFilterRel),
                   
    )

class ReasonableDaysAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'promo',
                    'group', 'prof', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('promo', DropdownFilterAll),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('group', DropdownFilterRel),
                   ('prof', DropdownFilterRel),
    )

class StabilizeAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'promo', 'general',
                    'group', 'prof', 'module', 'nature', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('promo', DropdownFilterAll),                   
                   ('group', DropdownFilterRel),
                   ('prof', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('nature', DropdownFilterAll),
    )

class MinHalfDaysAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'prof', 'module', 'join2courses', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('prof', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   'join2courses',
    )


class MinNonPreferedSlotAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'prof', 'promo', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('prof', DropdownFilterRel),
                   ('promo', DropdownFilterAll),                   
    )



class AvoidBothSlotsAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'prof', 'prof', 'group',
                    'promo','slot1','slot2', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('promo', DropdownFilterAll),                   
                   ('prof', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('promo', DropdownFilterAll),                   
                   ('slot1', DropdownFilterRel),                   
                   ('slot2', DropdownFilterRel),                   
    )


class SimultaneousCoursesAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'course1', 'course2', 'comment')
    ordering = ()
    empty_value_display = 'All!'
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('course1', DropdownFilterRel),                   
                   ('course2', DropdownFilterRel),                   
    )




















admin.site.register(LimitNaturePerPeriod, LimitNaturePerPeriodAdmin)
admin.site.register(ReasonableDays, ReasonableDaysAdmin)
admin.site.register(Stabilize, StabilizeAdmin)
admin.site.register(MinHalfDays, MinHalfDaysAdmin)
admin.site.register(MinNonPreferedSlot, MinNonPreferedSlotAdmin)
admin.site.register(AvoidBothSlots, AvoidBothSlotsAdmin)
admin.site.register(SimultaneousCourses, SimultaneousCoursesAdmin)
