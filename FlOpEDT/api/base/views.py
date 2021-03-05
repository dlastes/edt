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
from drf_yasg.utils import swagger_auto_schema

from api.base import serializers
from rest_framework import viewsets
import django_filters.rest_framework as filters
import base.models as bm

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import *
from django.views.generic import TemplateView
from django.conf import settings
from django.utils.decorators import method_decorator
from api.shared.params import week_param, year_param, dept_param
from api.permissions import IsTutorOrReadOnly, IsAdminUserOrReadOnly

from api.permissions import IsTutorOrReadOnly, IsAdminUserOrReadOnly

# ------------
# -- GROUPS --
# ------------


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the departments

    Can be filtered as wanted with every field of a Department object.
    """
    permission_classes = [IsTutorOrReadOnly]

    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer


class GroupTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group types

    Can be filtered as wanted with every field of a GroupType object.
    """
    permission_classes = [IsTutorOrReadOnly]

    queryset = bm.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer


class GroupsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='train_prog__department__abbrev', required=True)

    class Meta:
        model = bm.Group
        fields = ['dept']


class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the groups

    Can be filtered as wanted with parameter="dept"[required] of a Group object, with the function GroupsFilterSet
    """
    permission_classes = [IsAdminUserOrReadOnly]
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
    permission_classes = [IsTutorOrReadOnly]

    queryset = bm.RoomType.objects.all()
    serializer_class = serializers.RoomTypesSerializer
    filterset_fields = '__all__'


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see a list which shows each room is with what kind of group.

    Can be filtered as wanted with every field of a Room object.
    """
    permission_classes = [IsTutorOrReadOnly]

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
    permission_classes = [IsTutorOrReadOnly]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomNameSerializer
    filter_class = RoomFilterSet


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the rooms.

    Can be filtered as wanted with parameter="dept"[required] of a Room object, with the function RoomsFilterSet
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    filter_class = RoomFilterSet

    # filterset_fields = '__all__'


class RoomSortsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room sorts.

    Can be filtered as wanted with every field of a RoomSort object.
    """
    permission_classes = [IsAdminUserOrReadOnly]
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
                           dept_param(required=True)])
)
class ModuleViewSet(viewsets.ModelViewSet):
    """
    Modules in a given department

    TODO: (Header for list)

    """
    permission_classes = [IsTutorOrReadOnly]
    
    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    filterset_fields = '__all__'

    def get_queryset(self):
        # Get the filters from the request
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        abbrev=self.request.query_params.get('dept', None)

        # Applying filters
        if week is not None and year is not None:
            # Those 2 filters are needed to have returned data
            # distinct method allows us to get each module only once
            qs = bm.ScheduledCourse.objects.distinct('course__module').filter(course__week=week, course__year=year)
            # Filtering with department
            qs = qs.filter(course__module__train_prog__department__abbrev=abbrev)

            # Getting every module that appears
            qs_module = qs.values('course__module')
            # Get all the modules that appears in the scheduled courses. Those primary keys come from the previous line
            return bm.Module.objects.filter(pk__in=qs_module)
        else:
            return bm.Module.objects.filter(train_prog__department__abbrev=abbrev)


class ModuleFullViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the modules that have a Scheduled course in a given week/year couple.

    can also be filtered with a department.
    """
    permission_classes = [IsTutorOrReadOnly]

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

    permission_classes = [IsTutorOrReadOnly]


class CourseTypeNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course types.

    Can be filtered as wanted with the department of a CourseType object, with the function CourseTypesFilterSet
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypeNameSerializer
    filter_class = CourseTypeFilterSet

    filterset_fields = '__all__'

    permission_classes = [IsTutorOrReadOnly]


class CoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses

    Can be filtered as wanted with every field of a Course object.
    """
    queryset = bm.Course.objects.all()
    serializer_class = serializers.CoursesSerializer

    filterset_fields = '__all__'

    permission_classes = [IsTutorOrReadOnly]

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

    permission_classes = [IsAdminUserOrReadOnly]


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


# ---------------
# --- OTHERS ----
# ---------------

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


class TrainingProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the training programs
    """
    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgrammeSerializer
    filterset_class = TrainingProgrammeFilterSet