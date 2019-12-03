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

class TutorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = '__all__'

class SupplyStaffsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.SupplyStaff
        fields = '__all__'

class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Student
        fields = '__all__'
"""
class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['morning_weight', 'free_half_day_weight']

class StudentPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['student', 'morning_weight', 'free_half_day_weight']

class GroupPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['group', 'morning_weight', 'free_half_day_weight']
"""
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

class RoomGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomGroup
        fields = '__all__'


class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Room
        fields = '__all__'

class RoomSortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomSort
        fields = '__all__'

# -------------
# -- COURSES --
# -------------

class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Module
        fields = '__all__'

class CourseTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseType
        fields = '__all__'

class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Course
        fields = '__all__'

# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.UserPreference
        fields = '__all__'

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

class PlanningModificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.PlanningModification
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


# ---------------
# ---- TTAPP ----
# ---------------

# class TTSlotsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ttm.Slot
#         fields = '__all__'

# class TTConstraintsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ttm.TTConstraint
#         fields = '__all__'

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


# ----------------------
# -- ScheduledCourses --
# ----------------------

class ModuleDisplaySCSerializer(serializers.Serializer):
    color_bg = serializers.CharField()
    color_txt = serializers.CharField()

    class Meta:
        model = dwm.ModuleDisplay
        fields = ['color_bg', 'color_txt']

class ModuleSCSerializer(serializers.Serializer):
    name = serializers.CharField()
    display = ModuleDisplaySCSerializer()

    class Meta:
        model = bm.Module
        fields = ['name', 'display']

class GroupSCSerializer(serializers.Serializer):
    train_prog = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = bm.Group
        fields = ['name', 'train_prog']

class CourseSCSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    tutor = serializers.CharField()
    room_type = serializers.CharField()
    week = serializers.IntegerField()
    year = serializers.IntegerField()
    group = GroupSCSerializer()
    module = ModuleSCSerializer()

    class Meta:
        model = bm.Course
        fields = ['id', 'type', 'tutor', 'room_type', 'week', 'year', 'module', 'group',]

class ScheduledCoursesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    room = serializers.CharField()
    start_time = serializers.IntegerField()
    course = CourseSCSerializer()

    class Meta:
        model = bm.ScheduledCourse
        fields = ['id', 'room', 'start_time', 'course']