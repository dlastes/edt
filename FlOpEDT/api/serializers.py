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

from rest_framework import serializers
import base.models as bm
import people.models as pm
import quote.models as q
import displayweb.models as dwm
import TTapp.models as ttm

# ------------
# -- PEOPLE --
# ------------
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'

class UserDepartmentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.UserDepartmentSettings
        fields = '__all__'

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = ['username', 'first_name', 'last_name', 'email']

class TutorUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = ['username']

class SupplyStaffsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.SupplyStaff
        fields = '__all__'

class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Student
        fields = '__all__'


class StudentPreferencesSerializer(serializers.Serializer):
    student = serializers.CharField()
    morning_weight = serializers.IntegerField()
    free_half_day_weight = serializers.IntegerField()

    class Meta:
        model = pm.Preferences
        fields = ['student', 'morning_weight', 'free_half_day_weight']

class GroupPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['group', 'morning_weight', 'free_half_day_weight']

# ------------
# -- GROUPS --
# ------------

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Department
        fields = '__all__'


class TrainingProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TrainingProgramme
        fields = '__all__'

class GroupTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupType
        fields = '__all__'

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Group
        fields = '__all__'


# ------------
# -- TIMING --
# ------------

class HolidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Holiday
        fields = '__all__'

class TrainingHalfDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TrainingHalfDay
        fields = '__all__'

class PeriodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Period
        fields = '__all__'

class TimeGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TimeGeneralSettings
        fields = '__all__'


# -----------
# -- ROOMS --
# -----------
class RoomTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomType
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Room
        fields = '__all__' #['id', 'name', 'subroom_of', 'departments'] 

class RoomNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Room
        fields = ['name'] 

class RoomSortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomSort
        fields = '__all__'

# -------------
# -- COURSES --
# -------------
class TrainingPrograms_M_Serializer(serializers.Serializer):
    abbrev= serializers.CharField()

    class Meta:
        model = bm.TrainingProgramme
        fields = ['abbrev', ]

class Period_M_Serializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Period
        fields = ['starting_week', 'ending_week', 'name']


class ModuleFullSerializer(serializers.ModelSerializer):
    train_prog = TrainingProgramsSerializer()
    period = Period_M_Serializer()

    class Meta:
        model = bm.Module
        fields = ['name', 'abbrev', 'head', 'ppn', 'url', 'train_prog', 'period']


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = bm.Module
        fields = ['name', 'abbrev', 'url']


class Department_Name_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.Department
        fields = ['name']

class CourseType_C_Serializer(serializers.Serializer):
    department = Department_Name_Serializer()
    name = serializers.CharField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'department']


class RoomType_C_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.RoomType
        fields = ['name']


class Group_C_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.Group
        fields = ['name']


class Module_C_Serializer(serializers.Serializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Module
        fields = ['abbrev']


class CoursesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    week = serializers.IntegerField()
    year = serializers.IntegerField()
    no = serializers.IntegerField()
    type = CourseType_C_Serializer()
    room_type = RoomType_C_Serializer()
    tutor = serializers.CharField()
    supp_tutor = serializers.CharField()
    group = Group_C_Serializer()
    module = Module_C_Serializer()
    modulesupp = Module_C_Serializer()


    class Meta:
        model = bm.Course
        fields = ['id', 'week', 'year', 'no', 'department', 'type',
                'room_type', 'tutor', 'supp_tutor', 'group', 'module', 'modulesupp']

# -----------------
# -- PREFERENCES --
# -----------------

class UserPreferenceSerializer(serializers.Serializer):
    user = serializers.CharField()
    week = serializers.IntegerField()
    year = serializers.IntegerField()
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        model = bm.UserPreference
        fields = ['user']

class CoursePreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CoursePreference
        fields = '__all__'

class RoomPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomPreference
        fields = '__all__'

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.EdtVersion
        fields = '__all__'

class CourseModificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseModification
        fields = '__all__'

# -----------
# -- COSTS --
# -----------

class TutorCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TutorCost
        fields = '__all__'

class GroupCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupCost
        fields = '__all__'

class GroupFreeHalfDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupFreeHalfDay
        fields = '__all__'

# ----------
# -- MISC --
# ----------

class DependenciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Dependency
        fields = '__all__'

class CourseStartTimeConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = '__all__'

class RegensSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Regen
        fields = '__all__'

# ----------
# -- QUOTE -
# ----------

class QuoteTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = q.QuoteType
        fields = '__all__'

class QuotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = q.Quote
        fields = '__all__'

# ---------------
# -- DISPLAYWEB -
# ---------------

class BreakingNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.BreakingNews
        fields = '__all__'

class ModuleDisplaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.ModuleDisplay
        fields = '__all__'

class TrainingProgrammeDisplaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.TrainingProgrammeDisplay
        fields = '__all__'

class GroupDisplaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.GroupDisplay
        fields = '__all__'


#
#   Log-in-and-out
#

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'

class LogoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'



# ---------------
# ---- TTAPP ----
# ---------------


class TTCustomConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.CustomConstraint
        fields = '__all__'

class TTLimitCourseTypeTimePerPeriodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.LimitCourseTypeTimePerPeriod
        fields = '__all__'

class TTReasonableDayssSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.ReasonableDays
        fields = '__all__'

class TTStabilizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.Stabilize
        fields = '__all__'

class TTMinHalfDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.MinHalfDays
        fields = '__all__'

class TTMinNonPreferedSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.MinNonPreferedSlot
        fields = '__all__'

class TTAvoidBothTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.AvoidBothTimes
        fields = '__all__'

class TTSimultaneousCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.SimultaneousCourses
        fields = '__all__'

class TTLimitedStartTimeChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.LimitedStartTimeChoices
        fields = '__all__'

class TTLimitedRoomChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.LimitedRoomChoices
        fields = '__all__'


#    --------------------------------------------------------------------------------
#   |                                                                                |
#   | ////////////////////////////////////////////////////////////////////////////// |
#   |                                                                                |
#   |                                     FETCHS                                     |
#   |                                                                                |
#   | ////////////////////////////////////////////////////////////////////////////// |
#   |                                                                                |
#    --------------------------------------------------------------------------------

#                             ------------------------------                            #
#                             ----Scheduled Courses (SC)----                            #
#                             ------------------------------                            #

class ModuleDisplay_SC_Serializer(serializers.Serializer):
    color_bg = serializers.CharField()
    color_txt = serializers.CharField()

    class Meta:
        model = dwm.ModuleDisplay
        fields = ['color_bg', 'color_txt']

class Module_SC_Serializer(serializers.Serializer):
    name = serializers.CharField()
    display = ModuleDisplay_SC_Serializer()

    class Meta:
        model = bm.Module
        fields = ['name', 'display']

class Group_SC_Serializer(serializers.Serializer):
    train_prog = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = bm.Group
        fields = ['name', 'train_prog']

class Course_SC_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    tutor = serializers.CharField()
    room_type = serializers.CharField()
    week = serializers.IntegerField()
    year = serializers.IntegerField()
    group = Group_SC_Serializer()
    module = Module_SC_Serializer()

    class Meta:
        model = bm.Course
        fields = ['id', 'type', 'tutor', 'room_type', 'week', 'year', 'module', 'group',]

class ScheduledCoursesSerializer(serializers.Serializer):
    # Spécification des champs voulus
    id = serializers.IntegerField()
    room = serializers.CharField()
    start_time = serializers.IntegerField()
    day = serializers.CharField()
    course = Course_SC_Serializer()

    # Mise en forme des données
    class Meta:
        model = bm.ScheduledCourse
        fields = ['id', 'room', 'start_time', 'day', 'course']

#                             -------------------------------                           #
#                             ----UnscheduledCourses (PP)----                           #
#                             -------------------------------                           #

class ModuleDisplay_PP_Serializer(serializers.Serializer):
    color_bg = serializers.CharField()
    color_txt = serializers.CharField()

    class Meta:
        model = dwm.ModuleDisplay
        fields = ['color_bg', 'color_txt']

class Group_PP_Serializer(serializers.Serializer):
    name = serializers.CharField()
    train_prog = serializers.CharField()

    class Meta:
        model = bm.Group
        fields = ['name', 'train_prog']

class ModuleCours_PP_Serializer(serializers.Serializer):
    abbrev = serializers.CharField()
    display = ModuleDisplay_PP_Serializer()

    class Meta:
        model = bm.Module
        fields = ['abbrev', 'display']

class CourseType_PP_Serializer(serializers.Serializer):
    name = serializers.CharField()
    duration = serializers.IntegerField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'duration']

class UnscheduledCoursesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tutor = serializers.CharField()
    room_type = serializers.CharField()
    module = ModuleCours_PP_Serializer()
    group = Group_PP_Serializer()
    type = CourseType_PP_Serializer()

    class Meta:
        model = bm.Course
        fields = ['id', 'tutor', 'room_type', 'module', 'group', ]

#                                ---------------------------                            #
#                                ----Availabilities (Av)----                            #
#                                ---------------------------                            #

class Tutor_Av_Serializer(serializers.Serializer):
    username = serializers.CharField()

    class Meta:
        model = pm.Tutor
        fields = ['username']

class AvailabilitiesSerializer(serializers.Serializer):
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()
    user = Tutor_Av_Serializer()

    class Meta:
        model = bm.UserPreference
        fields = ['day', 'start_time', 'duration', 'value', 'user']

#                                  --------------------                                 #
#                                  ----Default Week----                                 #
#                                  --------------------                                 #

class DefaultWeekSerializer(serializers.Serializer):
    user = serializers.CharField()
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        model = bm.UserPreference
        fields = ['user', 'day', 'start_time', 'duration', 'value']

#                              ---------------------------                              #
#                              ----Course Default Week----                              #
#                              ---------------------------                              #
#   No data to display

class CourseTypeDefaultWeekSerializer(serializers.Serializer):
    course_type = serializers.CharField()
    train_prog = serializers.CharField()
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        model = bm.CoursePreference
        fields = ['course_type', 'train_prog', 'day', 'start_time', 'duration', 'value']

#                                -------------------------                              #
#                                ----Training Programs----                              #
#                                -------------------------                              #

class TrainingProgrammeNameSerializer(serializers.ModelSerializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.TrainingProgramme
        fields = ['abbrev']


class TrainingProgrammeSerializer(serializers.ModelSerializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.TrainingProgramme
        fields = ['abbrev', 'name']

#                                -------------------------                              #
#                                ----Unavailable rooms----                              #
#                                -------------------------                              #
# Has to be done in the views of base folder. Need to be clarified

#                                 -----------------------                               #
#                                 ----All Tutors (AT)----                               #
#                                 -----------------------                               #

class User_AT_Serializer(serializers.Serializer):
    username = serializers.CharField()
    class Meta:
        model = pm.User
        fields = ['username']

#                                  -------------------                                  #
#                                  ----Departments----                                  #
#                                  -------------------                                  #

class DepartmentAbbrevSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Department
        fields = ['id', 'abbrev']

#                                  --------------------                                 #
#                                  ----All Versions----                                 #
#                                  --------------------                                 #

class AllVersionsSerializer(serializers.ModelSerializer):
    # Spécification des champs voulus
    year = serializers.IntegerField()
    week = serializers.IntegerField()
    version = serializers.IntegerField()
    department = DepartmentAbbrevSerializer()

    # Mise en forme des données
    class Meta:
        model = bm.EdtVersion
        fields = ['year', 'week', 'version', 'department']

#                               --------------------------                              #
#                               ----Tutor Courses (TC)----                              #
#                               --------------------------                              #

class Department_TC_Serializer(serializers.Serializer):
    name = serializers.CharField()
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Department
        fields = ['name', 'abbrev']

class CourseType_TC_Serializer(serializers.Serializer):
    department = Department_TC_Serializer()

    class Meta:
        model = bm.Course
        fields = ['department']


class Course_TC_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = CourseType_TC_Serializer()
    tutor = serializers.CharField()
    room_type = serializers.CharField()
    week = serializers.IntegerField()
    year = serializers.IntegerField()
    group = Group_SC_Serializer()
    module = Module_SC_Serializer()

    class Meta:
        model = bm.Course
        fields = ['id', 'type', 'tutor', 'room_type', 'week', 'year', 'module', 'group']


class TutorCourses_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    room = serializers.CharField()
    start_time = serializers.IntegerField()
    course = Course_TC_Serializer()

    class Meta:
        model = bm.ScheduledCourse
        fields = ['room', 'start_time', 'course']

#                           -------------------------------------                       #
#                           ----Extra Scheduled Courses (ESC)----                       #
#                           -------------------------------------                       #


class CourseType_ESC_Serializer(serializers.Serializer):
    duration = serializers.IntegerField()
    department = DepartmentAbbrevSerializer()

    class Meta:
        model = bm.CourseType
        fields = ['duration', 'department']

class Course_ESC_Serializer(serializers.Serializer):
    tutor = serializers.CharField()
    type = CourseType_ESC_Serializer()

    class Meta:
        model = bm.Course
        fields = ['tutor', 'type']

class ExtraScheduledCoursesSerializer(serializers.Serializer):
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    course = Course_ESC_Serializer()    

    class Meta:
        model = bm.ScheduledCourse
        fields = ['day', 'start_time', 'course']

#                                  --------------------                                 #
#                                  ----Shared Rooms----                                 #
#                                  --------------------                                 #

#                                  ---------------------                                #
#                                  ----Breaking News----                                #
#                                  ---------------------                                #

class BKNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.BreakingNews
        fields = ['id', 'x_beg', 'x_end', 'y', 'txt', 'fill_color', 'strk_color', 'is_linked']

#                                     --------------                                    #
#                                     ----Decale----                                    #
#                                     --------------                                    #

#                                  --------------------                                 #
#                                  ----Course Types----                                 #
#                                  --------------------                                 #

class CourseTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'duration']


class CourseTypeNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = bm.CourseType
        fields = ['name']

#                                     --------------                                    #
#                                     ----Groups----                                    #
#                                     --------------                                    #

#                                      -------------                                    #
#                                      ----Rooms----                                    #
#                                      -------------                                    #

#                                  -------------------                                  #
#                                  ----Constraints----                                  #
#                                  -------------------                                  #

#                                   ------------------                                  #
#                                   ----Week infos----                                  #
#                                   ------------------                                  #
