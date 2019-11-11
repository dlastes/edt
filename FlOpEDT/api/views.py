from rest_framework import viewsets
from api import serializers
from base import models

# ------------
# -- GROUPS --
# ------------

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the departments
    """
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer

class TrainingProgramsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the training programs
    """
    queryset = models.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgramsSerializer

class GroupTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group types
    """
    queryset = models.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer

class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the groups
    """
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupsSerializer

# ------------
# -- TIMING --
# ------------
class DaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the days
    """
    queryset = models.Day.objects.all()
    serializer_class = serializers.DaysSerializer

class SlotsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the slots
    """
    queryset = models.Slot.objects.all()
    serializer_class = serializers.SlotsSerializer

class HolidaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the holidays
    """
    queryset = models.Holiday.objects.all()
    serializer_class = serializers.HolidaysSerializer

class TrainingHalfDaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the half-day trainings
    """
    queryset = models.TrainingHalfDay.objects.all()
    serializer_class = serializers.TrainingHalfDaysSerializer

class PeriodsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the periods
    """
    queryset = models.Period.objects.all()
    serializer_class = serializers.PeriodsSerializer

class TimeGeneralSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the settings of time
    """
    queryset = models.TimeGeneralSettings.objects.all()
    serializer_class = serializers.TimeGeneralSettingsSerializer


# -----------
# -- ROOMS --
# -----------

class RoomTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room types
    """
    queryset = models.RoomType.objects.all()
    serializer_class = serializers.RoomTypesSerializer

class RoomGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room groups
    """
    queryset = models.RoomGroup.objects.all()
    serializer_class = serializers.RoomGroupsSerializer

class RoomsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the rooms
    """
    queryset = models.Room.objects.all()
    serializer_class = serializers.RoomsSerializer

class RoomSortsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room sorts
    """
    queryset = models.RoomSort.objects.all()
    serializer_class = serializers.RoomSortsSerializer

# -------------
# -- COURSES --
# -------------

class ModulesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the modules
    """
    queryset = models.Module.objects.all()
    serializer_class = serializers.ModulesSerializer

class CourseTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the course types
    """
    queryset = models.CourseType.objects.all()
    serializer_class = serializers.CourseTypesSerializer

class CoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the courses
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CoursesSerializer

class ScheduledCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the scheduled courses
    """
    queryset = models.ScheduledCourse.objects.all()
    serializer_class = serializers.ScheduledCoursesSerializer

# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the users' preferences
    """
    queryset = models.UserPreference.objects.all()
    serializer_class = serializers.UsersPreferencesSerializer

class CoursePreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the course preferences
    """
    queryset = models.CoursePreference.objects.all()
    serializer_class = serializers.CoursePreferencesSerializer

class RoomPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room preferences
    """
    queryset = models.RoomPreference.objects.all()
    serializer_class = serializers.RoomPreferencesSerializer

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the scheduler version
    """
    queryset = models.EdtVersion.objects.all()
    serializer_class = serializers.EdtVersionSerializer

class CourseModificationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the course modifications
    """
    queryset = models.CourseModification.objects.all()
    serializer_class = serializers.CourseModificationsSerializer

class PlanningModificationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the planning modifications
    """
    queryset = models.PlanningModification.objects.all()
    serializer_class = serializers.PlanningModificationsSerializer


# -----------
# -- COSTS --
# -----------

class TutorCostsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the tutor costs
    """
    queryset = models.TutorCost.objects.all()
    serializer_class = serializers.TutorCostsSerializer

class GroupCostsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group costs
    """
    queryset = models.GroupCost.objects.all()
    serializer_class = serializers.GroupCostsSerializer

class GroupFreeHalfDaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group's free half days
    """
    queryset = models.GroupFreeHalfDay.objects.all()
    serializer_class = serializers.GroupFreeHalfDaysSerializer


# ----------
# -- MISC --
# ----------

class DependenciesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the dependencies between courses
    """
    queryset = models.Dependency.objects.all()
    serializer_class = serializers.DependenciesSerializer

class CourseStartTimeConstraintsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the courses start time constraints
    """
    queryset = models.CourseStartTimeConstraint.objects.all()
    serializer_class = serializers.CourseStartTimeConstraintsSerializer

class RegensViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the regenerations
    """
    queryset = models.Regen.objects.all()
    serializer_class = serializers.RegensSerializer