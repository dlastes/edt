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

from api import serializers

from rest_framework import authentication, exceptions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import django_filters.rest_framework as filters

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import *
from django.views.generic import TemplateView
from django.conf import settings
from django.utils.decorators import method_decorator

import people.models as pm
import base.models as bm
import quote.models as p
import displayweb.models as dwm
import TTapp.models as ttm




# --------------------------------
# -- Frequently used parameters --
# --------------------------------

def week_param(**kwargs):
    return openapi.Parameter('week',
                             openapi.IN_QUERY,
                             description="week",
                             type=openapi.TYPE_INTEGER,
                             **kwargs)
def year_param(**kwargs):
    return openapi.Parameter('year',
                             openapi.IN_QUERY,
                             description="year",
                             type=openapi.TYPE_INTEGER,
                             **kwargs)
def user_param(**kwargs):
    return openapi.Parameter('user',
                             openapi.IN_QUERY,
                             description="username",
                             type=openapi.TYPE_STRING,
                             **kwargs)
def dept_param(**kwargs):
    return openapi.Parameter('dept',
                             openapi.IN_QUERY,
                             description="department abbreviation",
                             type=openapi.TYPE_STRING,
                             **kwargs)







# ------------
# -- PEOPLE --
# ------------
class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users

    Can be filtered as wanted with every field of a User object.
    """
    permission_classes = (IsAuthenticated,)
    queryset = pm.User.objects.all()
    serializer_class = serializers.UsersSerializer


class UserDepartmentSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the user department settings
    which shows the combination of the user and the department

    Can be filtered as wanted with every field of a User Department object.
    """
    queryset = pm.UserDepartmentSettings.objects.all()
    serializer_class = serializers.UserDepartmentSettingsSerializer


class SupplyStaffsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the supply staff

    Can be filtered as wanted with every field of a Supply Staff object.
    """
    queryset = pm.SupplyStaff.objects.all()
    serializer_class = serializers.SupplyStaffsSerializer


class StudentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the students

    Can be filtered as wanted with every field of a Student object.
    """
    queryset = pm.Student.objects.all()
    serializer_class = serializers.StudentsSerializer


# class StudentPreferencesViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet to see all the students' preferences.

#     Can be filtered as wanted with every field of a StudentPreference object.
#     """
#     permission_classes = (IsAuthenticated,)
#     serializer_class = serializers.StudentPreferencesSerializer
#     filterset_fields = '__all__'

#     def get_queryset(self):
#         # Creating a queryset containing every StudentPreference
#         qs = pm.StudentPreferences.objects.all()

#         # Getting the filters
#         username = self.request.query_params.get('username', None)

#         # Applying filters
#         if username == None:
#             return None
#         return qs.filter(username=username)


# class GroupPreferencesViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet to see all the groups' preferences.

#     Can be filtered as wanted with every field of a GroupPreference object.
#     """
#     permission_classes = (IsAuthenticated,)
#     queryset = pm.GroupPreferences.objects.all()
#     serializer_class = serializers.GroupPreferencesSerializer

# ------------
# -- GROUPS --
# ------------

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the departments

    Can be filtered as wanted with every field of a Department object.
    """
    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer


class GroupTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group types

    Can be filtered as wanted with every field of a GroupType object.
    """
    queryset = bm.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer


class GroupsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='train_prog__department__abbrev', required=True)

    class Meta:
        model = bm.Group
        fields = ['dept']


class GroupsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the groups

    Can be filtered as wanted with parameter="dept"[required] of a Group object, with the function GroupsFilterSet
    """
    serializer_class = serializers.GroupsSerializer
    queryset = bm.Group.objects.all()
    filter_class = GroupsFilterSet


# ------------
# -- TIMING --
# ------------

class HolidaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the holidays

    Can be filtered as wanted with every field of a Holidays object.
    """
    queryset = bm.Holiday.objects.all()
    serializer_class = serializers.HolidaysSerializer
    filterset_fields = '__all__'


class TrainingHalfDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the half-day trainings

    Can be filtered as wanted with every field of a TrainingHalfDay object.
    """
    queryset = bm.TrainingHalfDay.objects.all()
    serializer_class = serializers.TrainingHalfDaysSerializer

    filterset_fields = '__all__'


class PeriodsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the periods

    Can be filtered as wanted with every field of a Period object.
    """
    queryset = bm.Period.objects.all()
    serializer_class = serializers.PeriodsSerializer

    filterset_fields = '__all__'


class TimeGeneralFilter(filters.FilterSet):
    days = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = bm.TimeGeneralSettings
        fields = ('department', 'days')


class TimeGeneralSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the settings of time

    Can be filtered as wanted with parameter="days" of a TimeGeneralSetting object by calling the function TimeGeneralFilter
    """
    queryset = bm.TimeGeneralSettings.objects.all()
    serializer_class = serializers.TimeGeneralSettingsSerializer

    filterset_class = TimeGeneralFilter


# -----------
# -- ROOMS --
# -----------

class RoomTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room types

    Can be filtered as wanted with every field of a RoomTypes object.
    """
    queryset = bm.RoomType.objects.all()
    serializer_class = serializers.RoomTypesSerializer
    filterset_fields = '__all__'


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see a list which shows each room is with what kind of group.

    Can be filtered as wanted with every field of a Room object.
    """
    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    filterset_fields = '__all__'


class RoomFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='departments__abbrev', required=True)

    class Meta:
        model = bm.Room
        fields = ['dept']


class RoomNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see a list which shows each room is with what kind of group.

    Can be filtered as wanted with every field of a Room object.
    """
    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomNameSerializer
    filter_class = RoomFilterSet


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the rooms.

    Can be filtered as wanted with parameter="dept"[required] of a Room object, with the function RoomsFilterSet
    """
    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    filter_class = RoomFilterSet

    # filterset_fields = '__all__'


class RoomSortsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room sorts.

    Can be filtered as wanted with every field of a RoomSort object.
    """
    queryset = bm.RoomSort.objects.all()
    serializer_class = serializers.RoomSortsSerializer

    filterset_fields = '__all__'


# -------------
# -- COURSES --
# -------------

@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_description='If (week,year) is given, any module that is taught in this week',
        manual_parameters=[week_param(),
                           year_param(),
                           dept_param()])
)
class ModuleViewSet(viewsets.ModelViewSet):
    """
    Modules in a given department

    TODO: (Header for list)

    """
    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    filterset_fields = '__all__'

    def get_queryset(self):
        # Get the filters from the request
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        department = bm.Department.objects.get(
            abbrev=self.request.query_params.get('dept', None))

        # Applying filters
        if week is not None and year is not None:
            # Those 2 filters are needed to have returned data
            # distinct method allows us to get each module only once
            qs = bm.ScheduledCourse.objects.distinct('course__module').filter(course__week=week, course__year=year)
            # Filtering with department
            qs = qs.filter(course__module__train_prog__department=department)

            # Getting every module that appears
            qs_module = qs.values('course__module')
            # Get all the modules that appears in the scheduled courses. Those primary keys come from the previous line
            return bm.Module.objects.filter(pk__in=qs_module)
        else:
            return bm.Module.objects.filter(train_prog__department=department)


class ModuleFullViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the modules that have a Scheduled course in a given week/year couple.

    can also be filtered with a department.
    """
    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModuleFullSerializer
    filterset_fields = '__all__'


class CourseTypeFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='department__abbrev', required=True)

    class Meta:
        model = bm.CourseType
        fields = ['dept']


class CourseTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course types.

    Can be filtered as wanted with the department of a CourseType object, with the function CourseTypesFilterSet
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypeSerializer
    filter_class = CourseTypeFilterSet

    filterset_fields = '__all__'


class CourseTypeNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course types.

    Can be filtered as wanted with the department of a CourseType object, with the function CourseTypesFilterSet
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypeNameSerializer
    filter_class = CourseTypeFilterSet

    filterset_fields = '__all__'


class CoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses

    Can be filtered as wanted with every field of a Course object.
    """
    queryset = bm.Course.objects.all()
    serializer_class = serializers.CoursesSerializer

    filterset_fields = '__all__'


# -----------------
# -- PREFERENCES --
# -----------------

class CoursePreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course preferences.

    Can be filtered as wanted with every field of a CoursePreference object.
    """
    permission_classes = (IsAuthenticated,)
    queryset = bm.CoursePreference.objects.all()
    serializer_class = serializers.CoursePreferencesSerializer

    filterset_fields = '__all__'


# enabling only GET methods:
# from rest_framework import viewsets, mixins
# class Blabla(mixins.RetrieveModelMixin, viewsets.GenericViewSet)
# (cf https://stackoverflow.com/questions/23639113/disable-a-method-in-a-viewset-django-rest-framework)
#
# TODO check how to generate custom schema with this


class UserPreferenceGenViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserPreferenceSerializer


class UserPreferenceDefaultFilterSet(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username')
    dept = filters.CharFilter(field_name='user__departments__abbrev')

    class Meta:
        model = bm.UserPreference
        fields = ['user', 'dept']


class UserPreferenceDefaultViewSet(UserPreferenceGenViewSet):
    """
    ViewSet shows a User Preference Default List

    Can be filtered as wanted with "user"/"dept" of a UserPreference object.
    """
    permission_classes = (IsAuthenticated,)
    filter_class = UserPreferenceDefaultFilterSet
    queryset = bm.UserPreference.objects.filter(week=None)


class UserPreferenceSingularFilterSet(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username')
    dept = filters.CharFilter(field_name='user__departments__abbrev')
    # makes the fields required
    week = filters.NumberFilter(field_name='week', required=True)
    year = filters.NumberFilter(field_name='year', required=True)

    class Meta:
        model = bm.UserPreference
        fields = ['user', 'dept', 'week', 'year']


class UserPreferenceSingularViewSet(UserPreferenceGenViewSet):
    """
    ViewSet shows a User Preference Default List

    Can be filtered as wanted with "user"/"dept" of a UserPreference object.
    """
    permission_classes = (IsAuthenticated,)
    filter_class = UserPreferenceSingularFilterSet
    queryset = bm.UserPreference.objects.all()


class UserPreferenceActualFilterSet(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username')
    dept = filters.CharFilter(field_name='user__departments__abbrev')

    class Meta:
        model = bm.UserPreference
        fields = ['user', 'dept']


# Custom schema generation: see
# https://drf-yasg.readthedocs.io/en/stable/custom_spec.html
@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_description="Preferences from (week,year) if exist otherwise default week",
                       manual_parameters=[week_param(required=True),
                                          year_param(required=True),
                                          user_param(),
                                          dept_param()])
)
class UserPreferenceActualViewSet(UserPreferenceGenViewSet):
    #permission_classes = (IsAuthenticated,)
    #filter_class = UserPreferenceSingularFilterSet

    def get_query_params(self):
        # Getting the filters
        dict_params = {}
        week = self.request.query_params.get('week', None)
        if week is not None:
            dict_params['week'] = int(week)
        year = self.request.query_params.get('year', None)
        if year is not None:
            dict_params['year'] = int(year)
        user = self.request.query_params.get('user', None)
        if user is not None:
            dict_params['user__username'] = user
        dept = self.request.query_params.get('dept', None)
        if dept is not None:
            dict_params['user__departments__abbrev'] = dept
        return dict_params

    def get_queryset(self):
        params = self.get_query_params()
        print(params)
        qs = bm.UserPreference.objects.filter(**params)
        return qs


class RoomPreferenceDefaultFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='room__departments__abbrev')
    room = filters.CharFilter(field_name='room__name')

    class Meta:
        model = bm.RoomPreference
        fields = ['dept', 'room']


class RoomPreferenceDefaultViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room preferences

    Can be filtered as wanted with every field of a Room object.
    """
    permission_classes = (IsAuthenticated,)
    filter_class = RoomPreferenceDefaultFilterSet
    queryset = bm.RoomPreference.objects.filter(week=None)
    serializer_class = serializers.RoomPreferencesSerializer

class RoomPreferenceSingularFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='room__departments__abbrev', required=True)

    class Meta:
        model = bm.RoomPreference
        fields = ['dept']

class RoomPreferenceSingularViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_class = RoomPreferenceSingularFilterSet
    queryset = bm.RoomPreference.objects.filter()
    serializer_class = serializers.RoomPreferencesSerializer


# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduler version.

    Can be filtered as wanted with every field of a EDTVersion object.
    """
    queryset = bm.EdtVersion.objects.all()
    serializer_class = serializers.EdtVersionSerializer

    filterset_fields = '__all__'


class CourseModificationsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course modifications.

    Can be filtered as wanted with every field of a CourseModification object.
    """
    queryset = bm.CourseModification.objects.all()
    serializer_class = serializers.CourseModificationsSerializer

    filterset_fields = '__all__'


# -----------
# -- COSTS --
# -----------

class TutorCostsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the tutor costs.

    Can be filtered as wanted with every field of a TutorCost object.
    """
    queryset = bm.TutorCost.objects.all()
    serializer_class = serializers.TutorCostsSerializer

    filterset_fields = '__all__'


class GroupCostsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group costs.

    Can be filtered as wanted with every field of a GroupCost object.
    """
    queryset = bm.GroupCost.objects.all()
    serializer_class = serializers.GroupCostsSerializer

    filterset_fields = '__all__'


class GroupFreeHalfDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group's free half days.

    Can be filtered as wanted with every field of a GroupFreeHalfDay object.
    """
    queryset = bm.GroupFreeHalfDay.objects.all()
    serializer_class = serializers.GroupFreeHalfDaysSerializer

    filterset_fields = '__all__'


# ----------
# -- MISC --
# ----------

class DependenciesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the dependencies between courses.

    Can be filtered as wanted with every field of a Dependency object.
    """
    queryset = bm.Dependency.objects.all()
    serializer_class = serializers.DependenciesSerializer

    filterset_fields = '__all__'


class CoureStartTimeFilter(filters.FilterSet):
    """
    Custom filter for ArrayField allowed_start_times
    """
    allowed_start_times = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = ('course_type', 'allowed_start_times')


class CourseStartTimeConstraintsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses start time constraints.

    Can be filtered as wanted with "allowed_start_times"
    of a CourseStartTime object by using the function CoureStartTimeFilter
    """
    queryset = bm.CourseStartTimeConstraint.objects.all()
    serializer_class = serializers.CourseStartTimeConstraintsSerializer

    filterset_class = CoureStartTimeFilter


class RegenFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='department__abbrev', required=True)

    class Meta:
        model = bm.Regen
        fields = ['dept', 'year', 'week']


class RegensViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the regenerations.

    Can be filtered as wanted with "year"[required] / "week"[required] / "dept"[required]
    of a Regen object by calling the function RegensFilterSet
    """
    queryset = bm.Regen.objects.all()
    serializer_class = serializers.RegensSerializer
    filter_class = RegenFilterSet


# ----------
# -- QUOTE -
# ----------

class QuoteTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the quote types.

    Can be filtered as wanted with every field of a QuoteType object.
    """
    queryset = p.QuoteType.objects.all()
    serializer_class = serializers.QuoteTypesSerializer

    filterset_fields = '__all__'


class QuotesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the quotes.

    Can be filtered as wanted with every field of a Quote object.
    """
    queryset = p.Quote.objects.all()
    serializer_class = serializers.QuotesSerializer

    filterset_fields = '__all__'


# ---------------
# -- DISPLAYWEB -
# ---------------

class BreakingNewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the breaking news.

    Can be filtered as wanted with every field of a BreakingNews object.
    """
    queryset = dwm.BreakingNews.objects.all()
    serializer_class = serializers.BreakingNewsSerializer

    filterset_fields = '__all__'


class ModuleDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the module displays(the color of the background and the txt)

    Can be filtered as wanted with every field of a ModuleDisplay object.
    """
    queryset = dwm.ModuleDisplay.objects.all()
    serializer_class = serializers.ModuleDisplaysSerializer

    filterset_fields = '__all__'


class TrainingProgrammeDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programme displays.

    Can be filtered as wanted with every field of a TrainingProgrammeDisplay object.
    """
    queryset = dwm.TrainingProgrammeDisplay.objects.all()
    serializer_class = serializers.TrainingProgrammeDisplaysSerializer

    filterset_fields = '__all__'


class GroupDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group displays.

    Can be filtered as wanted with every field of a GroupDisplay object.
    """
    queryset = dwm.GroupDisplay.objects.all()
    serializer_class = serializers.GroupDisplaysSerializer
    filterset_fields = '__all__'


# ---------------
# ---- TTAPP ----
# ---------------


class TTCustomConstraintsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the TTCustomConstraints.

    Can be filtered as wanted with every field of a CustomContraint object.
    """
    queryset = ttm.CustomConstraint.objects.all()
    serializer_class = serializers.TTCustomConstraintsSerializer

    filterset_fields = '__all__'


class TTLimitCourseTypeTimePerPeriodsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the LimitCourseTypeTimePerPeriods.

    Can be filtered as wanted with every field of a LimitCourseTypeTimePerPeriods object.
    """
    queryset = ttm.LimitCourseTypeTimePerPeriod.objects.all()
    serializer_class = serializers.TTLimitCourseTypeTimePerPeriodsSerializer

    filterset_fields = '__all__'


class TTReasonableDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the ReasonableDays.

    Can be filtered as wanted with every field of a ReasonableDay object.
    """
    queryset = ttm.ReasonableDays.objects.all()
    serializer_class = serializers.TTReasonableDayssSerializer

    filterset_fields = '__all__'


class TTStabilizeFilter(filters.FilterSet):
    """
    Custom filter for ArrayField fixed_days
    """
    fixed_days = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ttm.Stabilize
        fields = ('group', 'module', 'tutor', 'fixed_days')


class TTStabilizeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the Stabilize objects from TTapp.

    Can be filtered as wanted with "fixed_days"
    of a Stabilize object by calling the function TTStabilizeFilter
    """
    queryset = ttm.Stabilize.objects.all()
    serializer_class = serializers.TTStabilizeSerializer

    filterset_class = TTStabilizeFilter


class TTMinHalfDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the MinHalfDays.

    Can be filtered as wanted with every field of a MinHalfDay object.
    """
    queryset = ttm.MinHalfDays.objects.all()
    serializer_class = serializers.TTMinHalfDaysSerializer

    filterset_fields = '__all__'


class TTMinNonPreferedSlotsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the MinNonPreferedSlots.

    Can be filtered as wanted with every field of a MinNonPreferedSlots object.
    """
    queryset = ttm.MinNonPreferedSlot.objects.all()
    serializer_class = serializers.TTMinNonPreferedSlotsSerializer

    filterset_fields = '__all__'


class TTAvoidBothTimesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the AvoidBothTimes.

    Can be filtered as wanted with every field of a AvoidBothTime object.
    """
    queryset = ttm.AvoidBothTimes.objects.all()
    serializer_class = serializers.TTAvoidBothTimesSerializer

    filterset_fields = '__all__'


class TTSimultaneousCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the SimultaneousCourses.

    Can be filtered as wanted with every field of a SimultaneousCourse object.
    """
    queryset = ttm.SimultaneousCourses.objects.all()
    serializer_class = serializers.TTSimultaneousCoursesSerializer

    filterset_fields = '__all__'


class TTLimitedFilter(filters.FilterSet):
    """
    Custom filter for ArrayField possible_start_times
    """
    possible_start_times = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ttm.LimitedStartTimeChoices
        fields = ('module', 'tutor', 'group', 'type', 'possible_start_times')


class TTLimitedStartTimeChoicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the LimitedStartTimeChoices.

    Can be filtered as wanted with "possible_start_times"
    of a LimitedStartChoices object by calling the function TTLimitedFilter
    """
    queryset = ttm.LimitedStartTimeChoices.objects.all()
    serializer_class = serializers.TTLimitedStartTimeChoicesSerializer

    filterset_class = TTLimitedFilter


class TTLimitedRoomChoicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the LimitedRoomChoices.

    Can be filtered as wanted with every field of a LimitedRoomChoice object.
    """
    queryset = ttm.LimitedRoomChoices.objects.all()
    serializer_class = serializers.TTLimitedRoomChoicesSerializer

    filterset_fields = '__all__'


# ---------------
# --- OTHERS ----
# ---------------
class ScheduledCourseFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='course__module__train_prog__department__abbrev', required=True)
    # makes the fields required
    week = filters.NumberFilter(field_name='course__week', required=True)
    year = filters.NumberFilter(field_name='course__year', required=True)

    # num_copy = filters.NumberFilter(field_name='num_copy')

    class Meta:
        model = bm.ScheduledCourse
        fields = ['dept', 'week', 'year']


class ScheduledCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduled courses

    Result can be filtered by function ScheduledCourseFilterSet
    as wanted with week, year and work_copy (0 by default).
    Request needs a department filter.
    """
    queryset = bm.ScheduledCourse.objects.all()
    serializer_class = serializers.ScheduledCoursesSerializer
    filter_class = ScheduledCourseFilterSet


class UnscheduledCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the unscheduled courses

    Result can be filtered as wanted with week, year, work_copy and department fields.
    """

    serializer_class = serializers.UnscheduledCoursesSerializer

    def get_queryset(self):
        # Creating querysets of all courses and all scheduled courses
        queryset_course = bm.Course.objects.all()
        queryset_sc = bm.ScheduledCourse.objects.all()

        # Getting filters from the URL params (?param1=...&param2=...&...)
        year = self.request.query_params.get('year', None)
        week = self.request.query_params.get('week', None)
        work_copy = self.request.query_params.get('work_copy', 0)
        department = self.request.query_params.get('department', None)

        # Filtering different querysets
        if year is not None:
            queryset_course = queryset_course.filter(year=year)

        if week is not None:
            queryset_course = queryset_course.filter(week=week)

        queryset_sc = queryset_sc.filter(work_copy=work_copy)
        if department is not None:
            queryset_course = queryset_course.filter(module__train_prog__department__abbrev=department)
            queryset_sc = queryset_sc.filter(course__module__train_prog__department__abbrev=department)

        # Getting courses values of ScheduledCourse objects
        queryset_sc = queryset_sc.values('course')

        # Finding unscheduled courses
        queryset = queryset_course.exclude(pk__in=queryset_sc)

        return queryset


class AvailabilitiesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the availabilities of the tutors.

    Result can be filtered as wanted with week, year and department fields.
    """
    serializer_class = serializers.AvailabilitiesSerializer

    def get_queryset(self):
        # Getting all the wanted data
        qs = bm.UserPreference.objects.all()

        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        dept = self.request.query_params.get('dept', None)

        # Filtering
        if week is not None:
            qs = qs.filter(week=week)
        if year is not None:
            qs = qs.filter(year=year)
        if dept is not None:
            qs = qs.filter(user__departments__abbrev=dept)

        return qs


class CourseTypeDefaultWeekViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduled courses

    Result can be filtered as wanted with the training program and the course type
    """
    serializer_class = serializers.CourseTypeDefaultWeekSerializer

    def get_queryset(self):
        # Getting the wanted data
        qs = bm.CoursePreference.objects.all()

        # Getting all the filters
        train_prog = self.request.query_params.get('train_prog', None)
        course_type = self.request.query_params.get('course_type', None)
        department = self.request.query_params.get('dept', None)

        # Filtering
        if department is not None:
            qs = qs.filter(train_prog__department=department)
        if train_prog is not None:
            qs = qs.filter(train_prog__abbrev=train_prog)
        if course_type is not None:
            qs = qs.filter(course_type__name=course_type)
        return qs


class TrainingProgrammeFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='department__abbrev', required=True)

    class Meta:
        model = bm.TrainingProgramme
        fields = ['dept']


class TrainingProgrammeNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programs
    """
    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgrammeNameSerializer
    filterset_class = TrainingProgrammeFilterSet


class TrainingProgrammeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programs
    """
    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgrammeSerializer
    filterset_class = TrainingProgrammeFilterSet


class TutorFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='departments__abbrev', required=True)

    class Meta:
        model = pm.Tutor
        fields = ['dept']


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_description="Active tutors",
                      manual_parameters=[week_param(), year_param()])
)
class TutorViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)

        # Filtering
        if week is not None and year is not None:
            return pm.Tutor.objects.filter(
                pk__in=bm.ScheduledCourse.objects.filter(
                    course__week=week,
                    course__year=year)\
                .distinct('tutor').values('tutor')
            )
        else:
            return pm.Tutor.objects.all()
    serializer_class = serializers.TutorSerializer
    filter_class = TutorFilterSet


class TutorUsernameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the tutors

    Can be filtered as wanted with every field of a Tutor object.
    """
    queryset = pm.Tutor.objects.all()
    serializer_class = serializers.TutorUsernameSerializer
    filter_class = TutorFilterSet


class AllVersionsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='department__abbrev')

    class Meta:
        model = bm.EdtVersion
        fields = ['dept']


class AllVersionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the versions of the Scheduler

    Result can be filtered as wanted with the department
    by using the function AllVersionsFilterSet
    """
    queryset = bm.EdtVersion.objects.all()
    serializer_class = serializers.AllVersionsSerializer
    filter_class = AllVersionsFilterSet


class DepartmentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the departments

    Can be filtered as wanted with every field of a Department object.
    """
    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentAbbrevSerializer

    filterset_fields = '__all__'


class TutorCoursesFilterSet(filters.FilterSet):
    tutor_name = filters.CharFilter(field_name='user__departments__train_pro__module__module__tutor__username',
                                    required=True)
    year = filters.CharFilter(field_name='user__departments__train_pro__module__module__year')
    week = filters.CharFilter(field_name='user__departments__train_pro__module__module__week')
    dept = filters.CharFilter(field_name='user__departments__abbrev')

    class Meta:
        model = pm.UserDepartmentSettings
        fields = ['tutor_name', 'year', 'week', 'dept']


class TutorCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses of a tutor

    Result needs to be filtered by the username of a tutor.
    Filtering is also possible with week, department and year.
    """
    serializer_class = serializers.TutorCourses_Serializer
    queryset = pm.UserDepartmentSettings.objects.all()
    filter_class = TutorCoursesFilterSet


class ExtraSchedCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the Scheduled courses of a tutor in an other department

    Result can be filtered with year and week
    """
    serializer_class = serializers.ExtraScheduledCoursesSerializer

    def get_queryset(self):
        qs = bm.ScheduledCourse.objects.all()
        qs_esc = bm.ScheduledCourse.objects.all()
        # Getting all the filters
        user = self.request.query_params.get('username', None)
        dept = self.request.query_params.get('dept', None)
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)

        # Filtering
        if user is None:
            return None
        if dept is None:
            return None

        if week is not None:
            qs_esc = qs_esc.filter(course__week=week)
            qs = qs.filter(course__week=week)
        if year is not None:
            qs_esc = qs_esc.filter(course__year=year)
            qs = qs.filter(course__year=year)

        # Getting all the needed data
        qs.filter(course__tutor__username=user, course__module__train_prog__department__abbrev=dept)
        qs_esc.filter(course__tutor__username=user).exclude(pk__in=qs)

        return qs_esc


class BKNewsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='department__abbrev', required=True)
    # makes the fields required
    week = filters.NumberFilter(field_name='week', required=True)
    year = filters.NumberFilter(field_name='year', required=True)

    class Meta:
        model = dwm.BreakingNews
        fields = ['dept', 'week', 'year']


class BKNewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the BKNews

    Result needs to be filtered by the department,the week and the year.
    """
    queryset = dwm.BreakingNews.objects.all()
    serializer_class = serializers.BKNewsSerializer
    filter_class = BKNewsFilterSet


class LoginView(TemplateView):
    template_name = 'login.html'
    queryset = ''
    serializer_class = serializers.LoginSerializer

    def post(self, request, **kwargs):
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)  # Bon URL à mettre

        return render(request, self.template_name)

    def get_extra_actions():
        return []


class LogoutView(TemplateView):
    template_name = 'login.html'
    queryset = ''
    serializer_class = serializers.LogoutSerializer

    def get(self, request, **kwargs):
        logout(request)

        return render(request, self.template_name)

    def get_extra_actions():
        return []



