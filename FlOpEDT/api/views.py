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

from rest_framework import viewsets
import django_filters.rest_framework
from api import serializers
import people.models as pm
import base.models as bm
import quote.models as p
import displayweb.models as dwm
import TTapp.models as ttm
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import *
from django.views.generic import TemplateView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated 


# ------------
# -- PEOPLE --
# ------------
class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users
    """
    permission_classes = (IsAuthenticated,)    
    
    queryset = pm.User.objects.all()
    serializer_class = serializers.UsersSerializer
    

class UserDepartmentSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the user department settings
    """
    queryset = pm.UserDepartmentSettings.objects.all()
    serializer_class = serializers.UserDepartmentSettingsSerializer
    

class TutorsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the tutors
    """
    queryset = pm.Tutor.objects.all()
    serializer_class = serializers.TutorsSerializer
    

class SupplyStaffsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the supply staff
    """
    queryset = pm.SupplyStaff.objects.all()
    serializer_class = serializers.SupplyStaffsSerializer
    

class StudentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the students
    """
    queryset = pm.Student.objects.all()
    serializer_class = serializers.StudentsSerializer
    

#class PreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users' preferences
    """
    #queryset = pm.Preferences.objects.all()
    #serializer_class = serializers.PreferencesSerializer

#class StudentPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the students' preferences
    """
    #queryset = pm.StudentPreferences.objects.all()
    #serializer_class = serializers.StudentPreferencesSerializer

#class GroupPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the groups' preferences
    """
    #queryset = pm.GroupPreferences.objects.all()
    #serializer_class = serializers.GroupPreferencesSerializer

# ------------
# -- GROUPS --
# ------------

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the departments
    """
    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    

class TrainingProgramsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programs
    """
    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgramsSerializer
    

class GroupTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group types
    """
    queryset = bm.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer
    

class GroupsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the groups
    """
    queryset = bm.Group.objects.all()
    serializer_class = serializers.GroupsSerializer
    

# ------------
# -- TIMING --
# ------------

class HolidaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the holidays
    """
    queryset = bm.Holiday.objects.all()
    serializer_class = serializers.HolidaysSerializer
    
    filterset_fields = '__all__'

class TrainingHalfDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the half-day trainings
    """
    queryset = bm.TrainingHalfDay.objects.all()
    serializer_class = serializers.TrainingHalfDaysSerializer
    
    filterset_fields = '__all__'

class PeriodsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the periods
    """
    queryset = bm.Period.objects.all()
    serializer_class = serializers.PeriodsSerializer
    
    filterset_fields = '__all__'

class TimeGeneralSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the settings of time
    """
    queryset = bm.TimeGeneralSettings.objects.all()
    serializer_class = serializers.TimeGeneralSettingsSerializer
    
    filterset_fields = '__all__'


# -----------
# -- ROOMS --
# -----------

class RoomTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room types
    """
    queryset = bm.RoomType.objects.all()
    serializer_class = serializers.RoomTypesSerializer
    
    filterset_fields = '__all__'

class RoomGroupsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room groups
    """
    queryset = bm.RoomGroup.objects.all()
    serializer_class = serializers.RoomGroupsSerializer
    
    filterset_fields = '__all__'

class RoomsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the rooms
    """
    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomsSerializer
    
    filterset_fields = '__all__'

class RoomSortsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room sorts
    """
    queryset = bm.RoomSort.objects.all()
    serializer_class = serializers.RoomSortsSerializer
    
    filterset_fields = '__all__'

# -------------
# -- COURSES --
# -------------

class ModulesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the modules
    """
    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModulesSerializer
    
    filterset_fields = '__all__'

class CourseTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course types
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypesSerializer
    
    filterset_fields = '__all__'

class CoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses
    """
    queryset = bm.Course.objects.all()
    serializer_class = serializers.CoursesSerializer
    
    filterset_fields = '__all__'



# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users' preferences
    """
    queryset = bm.UserPreference.objects.all()
    serializer_class = serializers.UsersPreferencesSerializer
    filterset_fields = '__all__'

class CoursePreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course preferences
    """
    queryset = bm.CoursePreference.objects.all()
    serializer_class = serializers.CoursePreferencesSerializer
    
    filterset_fields = '__all__'

class RoomPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room preferences
    """
    queryset = bm.RoomPreference.objects.all()
    serializer_class = serializers.RoomPreferencesSerializer
    
    filterset_fields = '__all__'

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduler version
    """
    queryset = bm.EdtVersion.objects.all()
    serializer_class = serializers.EdtVersionSerializer
    
    filterset_fields = '__all__'

class CourseModificationsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course modifications
    """
    queryset = bm.CourseModification.objects.all()
    serializer_class = serializers.CourseModificationsSerializer
    
    filterset_fields = '__all__'

class PlanningModificationsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the planning modifications
    """
    queryset = bm.PlanningModification.objects.all()
    serializer_class = serializers.PlanningModificationsSerializer
    
    filterset_fields = '__all__'


# -----------
# -- COSTS --
# -----------

class TutorCostsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the tutor costs
    """
    queryset = bm.TutorCost.objects.all()
    serializer_class = serializers.TutorCostsSerializer
    
    filterset_fields = '__all__'

class GroupCostsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group costs
    """
    queryset = bm.GroupCost.objects.all()
    serializer_class = serializers.GroupCostsSerializer
    
    filterset_fields = '__all__'

class GroupFreeHalfDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group's free half days
    """
    queryset = bm.GroupFreeHalfDay.objects.all()
    serializer_class = serializers.GroupFreeHalfDaysSerializer
    
    filterset_fields = '__all__'


# ----------
# -- MISC --
# ----------

class DependenciesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the dependencies between courses
    """
    queryset = bm.Dependency.objects.all()
    serializer_class = serializers.DependenciesSerializer
    
    filterset_fields = '__all__'

class CourseStartTimeConstraintsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses start time constraints
    """
    queryset = bm.CourseStartTimeConstraint.objects.all()
    serializer_class = serializers.CourseStartTimeConstraintsSerializer
    
    filterset_fields = '__all__'

class RegensViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the regenerations
    """
    queryset = bm.Regen.objects.all()
    serializer_class = serializers.RegensSerializer
    
    filterset_fields = '__all__'

# ----------
# -- QUOTE -
# ----------

class QuoteTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the quote types
    """
    queryset = p.QuoteType.objects.all()
    serializer_class = serializers.QuoteTypesSerializer
    
    filterset_fields = '__all__'

class QuotesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the quotes
    """
    queryset = p.Quote.objects.all()
    serializer_class = serializers.QuotesSerializer
    
    filterset_fields = '__all__'

# ---------------
# -- DISPLAYWEB -
# ---------------

class BreakingNewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the breaking news
    """
    queryset = dwm.BreakingNews.objects.all()
    serializer_class = serializers.BreakingNewsSerializer
    
    filterset_fields = '__all__'

class ModuleDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the module displays
    """
    queryset = dwm.ModuleDisplay.objects.all()
    serializer_class = serializers.ModuleDisplaysSerializer
    
    filterset_fields = '__all__'

class TrainingProgrammeDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programme displays
    """
    queryset = dwm.TrainingProgrammeDisplay.objects.all()
    serializer_class = serializers.TrainingProgrammeDisplaysSerializer
    
    filterset_fields = '__all__'

class GroupDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group displays
    """
    queryset = dwm.GroupDisplay.objects.all()
    serializer_class = serializers.GroupDisplaysSerializer
    
    filterset_fields = '__all__'


# ---------------
# ---- TTAPP ----
# ---------------

# class TTSlotsViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet to see all the TTapp slots
#     """
#     queryset = ttm.Slot.objects.all()
#     serializer_class = serializers.TTSlotsSerializer
    
#     filterset_fields = '__all__'

# class TTConstraintsViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet to see all the TTContraints
#     """
#     queryset = ttm.TTConstraint.objects.all()
#     serializer_class = serializers.TTConstraintsSerializer
    
#     filterset_fields = '__all__'

class TTCustomConstraintsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the TTCustomConstraints
    """
    queryset = ttm.CustomConstraint.objects.all()
    serializer_class = serializers.TTCustomConstraintsSerializer
    
    filterset_fields = '__all__'

class TTLimitCourseTypeTimePerPeriodsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the LimitCourseTypeTimePerPeriods
    """
    queryset = ttm.LimitCourseTypeTimePerPeriod.objects.all()
    serializer_class = serializers.TTLimitCourseTypeTimePerPeriodsSerializer
    
    filterset_fields = '__all__'

class TTReasonableDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the ReasonableDays
    """
    queryset = ttm.ReasonableDays.objects.all()
    serializer_class = serializers.TTReasonableDayssSerializer
    
    filterset_fields = '__all__'

class TTStabilizeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the Stabilize objects from TTapp
    """
    queryset = ttm.Stabilize.objects.all()
    serializer_class = serializers.TTStabilizeSerializer
    
    filterset_fields = '__all__'

class TTMinHalfDaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the MinHalfDays
    """
    queryset = ttm.MinHalfDays.objects.all()
    serializer_class = serializers.TTMinHalfDaysSerializer
    
    filterset_fields = '__all__'

class TTMinNonPreferedSlotsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the MinNonPreferedSlots
    """
    queryset = ttm.MinNonPreferedSlot.objects.all()
    serializer_class = serializers.TTMinNonPreferedSlotsSerializer
    
    filterset_fields = '__all__'

class TTAvoidBothTimesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the AvoidBothTimes
    """
    queryset = ttm.AvoidBothTimes.objects.all()
    serializer_class = serializers.TTAvoidBothTimesSerializer
    
    filterset_fields = '__all__'

class TTSimultaneousCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the SimultaneousCourses
    """
    queryset = ttm.SimultaneousCourses.objects.all()
    serializer_class = serializers.TTSimultaneousCoursesSerializer
    
    filterset_fields = '__all__'

class TTLimitedStartTimeChoicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the LimitedStartTimeChoices
    """
    queryset = ttm.LimitedStartTimeChoices.objects.all()
    serializer_class = serializers.TTLimitedStartTimeChoicesSerializer
    
    filterset_fields = '__all__'

class TTLimitedRoomChoicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the LimitedRoomChoices
    """
    queryset = ttm.LimitedRoomChoices.objects.all()
    serializer_class = serializers.TTLimitedRoomChoicesSerializer
    
    filterset_fields = '__all__'


# ---------------
# --- OTHERS ----
# ---------------
class ScheduledCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduled courses

    Result can be filtered as wanted with week, year, work_copy and department fields.
    """
    serializer_class = serializers.ScheduledCoursesSerializer

    def get_queryset(self):
        # Creating a default queryset
        queryset = bm.ScheduledCourse.objects.all()

        # Getting filters from the URL params (?param1=...&param2=...&...)
        year = self.request.query_params.get('year', None)
        week = self.request.query_params.get('week', None)
        work_copy = self.request.query_params.get('work_copy', None)
        department = self.request.query_params.get('department', None)

        # Filtering
        if year is not None:
            queryset = queryset.filter(course__year=year)
        if week is not None:
            queryset=queryset.filter(course__week=week)
        if work_copy is not None:
            queryset = queryset.filter(work_copy=work_copy)
        if department is not None:
            queryset = queryset.filter(course__module__train_prog__department__abbrev=department)

        return queryset
        

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
        work_copy = self.request.query_params.get('work_copy', None)
        department = self.request.query_params.get('department', None)

        # Filtering different querysets
        if year is not None:
            queryset_course = queryset_course.filter(year=year)
        if week is not None:
            queryset_course=queryset_course.filter(week=week)
        if work_copy is not None:
            queryset_sc = queryset_sc.filter(work_copy=work_copy)
        if department is not None:
            queryset_course = queryset_course.filter(module__train_prog__department__abbrev=department)
            queryset_sc = queryset_sc.filter(course__module__train_prog__department__abrrev=department)

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
        ...


class DefaultWeekViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduled courses
    """
    queryset = bm.UserPreference.objects.filter(user__username="AB")
    serializer_class = serializers.DefaultWeekSerializer
    filterset_fields = '__all__'


class CourseDefaultWeekViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduled courses
    """
    queryset = bm.CoursePreference.objects.all()
    serializer_class = serializers.CourseDefaultWeekSerializer
    filterset_fields = '__all__'


class TrainingProgrammesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programs 
    """
    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgramsSerializer
    filterset_fields = '__all__'


class AllTutorsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programs 
    """
    queryset = pm.UserDepartmentSettings.objects.all()
    serializer_class = serializers.AllTutorsSerializer
    filterset_fields = '__all__'


class AllVersionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduler version
    """
    queryset = bm.EdtVersion.objects.all()
    serializer_class = serializers.AllVersionsSerializer
    
    filterset_fields = '__all__'


class DepartmentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduler version
    """
    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentAbbrevSerializer
    
    filterset_fields = '__all__'   


class TutorCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses of a tutor
    """
    queryset = bm.ScheduledCourse.objects.filter(course__week=50)
    serializer_class = serializers.TutorCourses_Serializer
    filterset_fields = '__all__'

class ExtraSchedCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses of a tutor
    """
    queryset = bm.ScheduledCourse.objects.filter(course__week=36)
    serializer_class = serializers.ExtraScheduledCoursesSerializer
    filterset_fields = '__all__'
    #get_queryset method needs to filter as the view does


class BKNewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses of a tutor
    """
    queryset = dwm.BreakingNews.objects.all()
    serializer_class = serializers.BKNewsSerializer

    filterset_fields = '__all__'


class AllCourseTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduler version
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.AllCourseTypesSerializer
    
    filterset_fields = '__all__'




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
        return HttpResponseRedirect( settings.LOGIN_REDIRECT_URL ) #Bon URL à mettre

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

