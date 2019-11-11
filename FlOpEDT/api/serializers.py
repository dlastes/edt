from rest_framework import serializers
from base import models

# ------------
# -- GROUPS --
# ------------

class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Department
        fields = ['name', 'abbrev']


class TrainingProgramsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TrainingProgramme
        fields = ['name', 'abbrev', 'department']

class GroupTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.GroupType
        fields = ['name', 'department']

class GroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Group
        fields = ['nom', 'train_prog', 'type', 'size', 'basic', 'parent_groups']


# ------------
# -- TIMING --
# ------------

class DaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Day
        fields = ['no', 'day']

class SlotsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Slot
        fields = ['jour', 'heure', 'duration']

class HolidaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Holiday
        fields = ['day', 'week', 'year']

class TrainingHalfDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TrainingHalfDay
        fields = ['apm', 'day', 'week', 'year', 'train_prog']

class PeriodsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Period
        fields = ['name', 'department', 'starting_week', 'ending_week']

class TimeGeneralSettingsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TimeGeneralSettings
        fields = ['department', 'day_start_time', 'day_finish_time', 'lunch_break_start_time', 'lunch_break_finish_time', 'days', 'default_preference_duration']


# -----------
# -- ROOMS --
# -----------
class RoomTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RoomType
        fields = ['department', 'name']

class RoomGroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RoomGroup
        fields = ['name', 'types']


class RoomsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Room
        fields = ['name', 'subroom_of', 'departments']

class RoomSortsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RoomSort
        fields = ['for_type', 'prefer', 'unprefer']

# -------------
# -- COURSES --
# -------------

class ModulesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Module
        # TODO: 'head', 'period'
        fields = ['nom', 'abbrev', 'ppn', 'train_prog']

class CourseTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CourseType
        fields = ['name', 'department', 'duration', 'group_types']

class CoursesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Course
        # TODO: 'tutor', 'supp_tutor', 'semaine', 'an'
        fields = ['type', 'room_type', 'no', 'groupe', 'module', 'modulesupp', 'suspens']

class ScheduledCoursesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ScheduledCourse
        fields = ['cours', 'day', 'start_time', 'room', 'no', 'noprec', 'copie_travail']

# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.UserPreference
        # TODO: 'user'
        fields = ['semaine', 'an', 'day', 'start_time', 'duration', 'valeur']

class CoursePreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CoursePreference
        fields = ['course_type', 'train_prog', 'semaine', 'an', 'day', 'start_time', 'duration', 'valeur']

class RoomPreferencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RoomPreference
        fields = ['room', 'semaine', 'an', 'day', 'start_time', 'duration', 'valeur']

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EdtVersion
        fields = ['department', 'semaine', 'an', 'version']

class CourseModificationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CourseModification
        # TODO: 'initiator'
        fields = ['cours', 'semaine_old', 'an_old', 'room_old', 'day_old', 'start_time_old', 'version_old', 'updated_at']

class PlanningModificationsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PlanningModification
        # TODO: 'initiator', 'tutor_old'
        fields = ['cours', 'semaine_old', 'an_old', 'updated_at']


# -----------
# -- COSTS --
# -----------

class TutorCostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TutorCost
        # TODO: 'tutor'
        fields = ['department', 'semaine', 'an', 'valeur', 'work_copy']

class GroupCostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.GroupCost
        fields = ['semaine', 'an', 'groupe', 'valeur', 'work_copy']

class GroupFreeHalfDaysSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.GroupFreeHalfDay
        fields = ['semaine', 'an', 'groupe', 'DJL', 'work_copy']

# ----------
# -- MISC --
# ----------

class DependenciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Dependency
        fields = ['cours1', 'cours2', 'successifs', 'ND']

class CourseStartTimeConstraintsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CourseStartTimeConstraint
        fields = ['course_type', 'allowed_start_times']

class RegensSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Regen
        fields = ['department', 'semaine', 'an', 'full', 'fday', 'fmonth', 'fyear', 'stabalise', 'sday', 'smonth', 'syear']