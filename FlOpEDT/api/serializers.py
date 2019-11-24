from rest_framework import serializers
import base.models as bm
import people.models as pm
import quote.models as q
import displayweb.models as dwm

# ------------
# -- PEOPLE --
# ------------
class UsersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'

class UserDepartmentSettingsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.UserDepartmentSettings
        fields = '__all__'

class TutorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = '__all__'

class SupplyStaffsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.SupplyStaff
        fields = '__all__'

class StudentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Student
        fields = '__all__'
"""
class PreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['morning_weight', 'free_half_day_weight']

class StudentPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['student', 'morning_weight', 'free_half_day_weight']

class GroupPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['group', 'morning_weight', 'free_half_day_weight']
"""
# ------------
# -- GROUPS --
# ------------

class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Department
        fields = '__all__'


class TrainingProgramsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TrainingProgramme
        fields = '__all__'

class GroupTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.GroupType
        fields = '__all__'

class GroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Group
        fields = '__all__'


# ------------
# -- TIMING --
# ------------

class DaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Day
        fields = '__all__'

class SlotsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Slot
        fields = '__all__'

class HolidaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Holiday
        fields = '__all__'

class TrainingHalfDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TrainingHalfDay
        fields = '__all__'

class PeriodsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Period
        fields = '__all__'

class TimeGeneralSettingsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TimeGeneralSettings
        fields = '__all__'


# -----------
# -- ROOMS --
# -----------
class RoomTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomType
        fields = '__all__'

class RoomGroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomGroup
        fields = '__all__'


class RoomsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Room
        fields = '__all__'

class RoomSortsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomSort
        fields = '__all__'

# -------------
# -- COURSES --
# -------------

class ModulesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Module
        fields = '__all__'

class CourseTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CourseType
        fields = '__all__'

class CoursesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Course
        fields = '__all__'

class ScheduledCoursesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.ScheduledCourse
        fields = '__all__'

# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.UserPreference
        fields = '__all__'

class CoursePreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CoursePreference
        fields = '__all__'

class RoomPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomPreference
        fields = '__all__'

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.EdtVersion
        fields = '__all__'

class CourseModificationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CourseModification
        fields = '__all__'

class PlanningModificationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.PlanningModification
        fields = '__all__'


# -----------
# -- COSTS --
# -----------

class TutorCostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TutorCost
        fields = '__all__'

class GroupCostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.GroupCost
        fields = '__all__'

class GroupFreeHalfDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.GroupFreeHalfDay
        fields = '__all__'

# ----------
# -- MISC --
# ----------

class DependenciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Dependency
        fields = '__all__'

class CourseStartTimeConstraintsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = '__all__'

class RegensSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Regen
        fields = '__all__'

# ----------
# -- QUOTE -
# ----------

class QuoteTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = q.QuoteType
        fields = '__all__'

class QuotesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = q.Quote
        fields = '__all__'

# ---------------
# -- DISPLAYWEB -
# ---------------

class BreakingNewsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = dwm.BreakingNews
        fields = '__all__'

class ModuleDisplaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = dwm.ModuleDisplay
        fields = '__all__'

class TrainingProgrammeDisplaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = dwm.TrainingProgrammeDisplay
        fields = '__all__'

class GroupDisplaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = dwm.GroupDisplay
        fields = '__all__'
