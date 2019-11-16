from rest_framework import serializers
import base.models as bm
import people.models as pm

# ------------
# -- PEOPLE --
# ------------
class UsersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.User
        fields = ['username', 'is_student', 'is_tutor', 'rights', 'departments']

class UserDepartmentSettingsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.UserDepartmentSettings
        fields = ['user', 'department', 'is_main']

class TutorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = ['username', 'first_name', 'last_name', 'email', 'rights', 'status', 'pref_hours_per_day', 'max_hours_per_day']

class SupplyStaffsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.SupplyStaff
        fields = ['username', 'first_name', 'last_name', 'email', 'rights', 'employer', 'position', 'field']

class StudentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = pm.Student
        fields = ['username', 'first_name', 'last_name', 'email', 'rights', 'belong_to']
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
        fields = ['name', 'abbrev']


class TrainingProgramsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TrainingProgramme
        fields = ['name', 'abbrev', 'department']

class GroupTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.GroupType
        fields = ['name', 'department']

class GroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Group
        fields = ['nom', 'train_prog', 'type', 'size', 'basic', 'parent_groups']


# ------------
# -- TIMING --
# ------------

class DaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Day
        fields = ['no', 'day']

class SlotsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Slot
        fields = ['jour', 'heure', 'duration']

class HolidaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Holiday
        fields = ['day', 'week', 'year']

class TrainingHalfDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TrainingHalfDay
        fields = ['apm', 'day', 'week', 'year', 'train_prog']

class PeriodsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Period
        fields = ['name', 'department', 'starting_week', 'ending_week']

class TimeGeneralSettingsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TimeGeneralSettings
        fields = ['department', 'day_start_time', 'day_finish_time', 'lunch_break_start_time', 'lunch_break_finish_time', 'days', 'default_preference_duration']


# -----------
# -- ROOMS --
# -----------
class RoomTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomType
        fields = ['department', 'name']

class RoomGroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomGroup
        fields = ['name', 'types']


class RoomsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Room
        fields = ['name', 'subroom_of', 'departments']

class RoomSortsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomSort
        fields = ['for_type', 'prefer', 'unprefer']

# -------------
# -- COURSES --
# -------------

class ModulesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Module
        fields = ['nom', 'abbrev', 'head', 'ppn', 'train_prog', 'period']

class CourseTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CourseType
        fields = ['name', 'department', 'duration', 'group_types']

class CoursesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Course
        fields = ['type', 'room_type', 'no', 'tutor', 'supp_tutor', 'groupe', 'module', 'modulesupp', 'semaine', 'an', 'suspens']

class ScheduledCoursesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.ScheduledCourse
        fields = ['cours', 'day', 'start_time', 'room', 'no', 'noprec', 'copie_travail']

# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.UserPreference
        fields = ['user', 'semaine', 'an', 'day', 'start_time', 'duration', 'valeur']

class CoursePreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CoursePreference
        fields = ['course_type', 'train_prog', 'semaine', 'an', 'day', 'start_time', 'duration', 'valeur']

class RoomPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.RoomPreference
        fields = ['room', 'semaine', 'an', 'day', 'start_time', 'duration', 'valeur']

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.EdtVersion
        fields = ['department', 'semaine', 'an', 'version']

class CourseModificationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CourseModification
        fields = ['cours', 'semaine_old', 'an_old', 'room_old', 'day_old', 'start_time_old', 'version_old', 'updated_at', 'initiator']

class PlanningModificationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.PlanningModification
        fields = ['cours', 'semaine_old', 'an_old', 'tutor_old', 'updated_at', 'initiator']


# -----------
# -- COSTS --
# -----------

class TutorCostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.TutorCost
        fields = ['department', 'semaine', 'an', 'tutor', 'valeur', 'work_copy']

class GroupCostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.GroupCost
        fields = ['semaine', 'an', 'groupe', 'valeur', 'work_copy']

class GroupFreeHalfDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.GroupFreeHalfDay
        fields = ['semaine', 'an', 'groupe', 'DJL', 'work_copy']

# ----------
# -- MISC --
# ----------

class DependenciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Dependency
        fields = ['cours1', 'cours2', 'successifs', 'ND']

class CourseStartTimeConstraintsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = ['course_type', 'allowed_start_times']

class RegensSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = bm.Regen
        fields = ['department', 'semaine', 'an', 'full', 'fday', 'fmonth', 'fyear', 'stabalise', 'sday', 'smonth', 'syear']