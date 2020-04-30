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




from django.contrib import admin
from base.admin import DepartmentModelAdmin

from TTapp.models import \
    LimitCourseTypeTimePerPeriod, Stabilize, \
    MinModulesHalfDays, MinTutorsHalfDays, MinGroupsHalfDays,\
    MinNonPreferedTrainProgsSlot, MinNonPreferedTutorsSlot, \
    CustomConstraint, SimultaneousCourses, MinimizeBusyDays, RespectBoundPerDay

# Register your models here.

# from TTapp.models import TestJour

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, \
    DropdownFilterCho


class CustomConstraintAdmin(DepartmentModelAdmin):
    list_display = ('class_name', 
                'week', 
                'year',
                'comment')
    ordering = ()
    list_filter = (('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   ('modules', DropdownFilterRel),
                   )   


class LimitCourseTypeTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('week', 
                    'year',
                    'course_type',
                    'max_hours',
                    'period', 
                    'comment')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class ReasonableDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   )


class StabilizeAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'general',
                    'group', 'tutor', 'module', 'type', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('type', DropdownFilterRel),
                   )


class MinTutorsHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'join2courses', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   'join2courses',
                   )


class MinModulesHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('modules', DropdownFilterRel),
                   )


class MinGroupsHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   )

    
    def get_field_queryset(self, db, db_field, request):

        queryset = super().get_field_queryset(db, db_field, request)

        if queryset and db_field.name == 'groups':
            return queryset.filter(basic=True).distinct()

        return queryset                          


class MinNonPreferedTutorsSlotAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )

class MinNonPreferedTrainProgsSlotAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   )


class AvoidBothTimesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'tutor', 'group', 'time1', 'time2', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('time1', DropdownFilterRel),
                   ('time2', DropdownFilterRel),
                   )


class SimultaneousCoursesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('courses', DropdownFilterRel),
                   )


class RespectBoundPerDayAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )


class MinimizeBusyDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )


admin.site.register(CustomConstraint, CustomConstraintAdmin)
admin.site.register(LimitCourseTypeTimePerPeriod, LimitCourseTypeTimePerPeriodAdmin)
#admin.site.register(ReasonableDays, ReasonableDaysAdmin)
admin.site.register(Stabilize, StabilizeAdmin)
admin.site.register(MinGroupsHalfDays, MinGroupsHalfDaysAdmin)
admin.site.register(MinTutorsHalfDays, MinTutorsHalfDaysAdmin)
admin.site.register(MinModulesHalfDays, MinModulesHalfDaysAdmin)
admin.site.register(MinNonPreferedTutorsSlot, MinNonPreferedTutorsSlotAdmin)
admin.site.register(MinNonPreferedTrainProgsSlot, MinNonPreferedTrainProgsSlotAdmin)
#admin.site.register(AvoidBothTimes, AvoidBothTimesAdmin)
admin.site.register(SimultaneousCourses, SimultaneousCoursesAdmin)
admin.site.register(MinimizeBusyDays, MinimizeBusyDaysAdmin)
admin.site.register(RespectBoundPerDay, RespectBoundPerDayAdmin)
