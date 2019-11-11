from rest_framework import viewsets
from api import serializers
import people.models as pm
import base.models as bm

# ------------
# -- PEOPLE --
# ------------
class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the users
    """
    queryset = pm.User.objects.all()
    serializer_class = serializers.UsersSerializer

class UserDepartmentSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the user department settings
    """
    queryset = pm.UserDepartmentSettings.objects.all()
    serializer_class = serializers.UserDepartmentSettingsSerializer

class TutorsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the tutors
    """
    queryset = pm.Tutor.objects.all()
    serializer_class = serializers.TutorsSerializer

class SupplyStaffsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the supply staff
    """
    queryset = pm.SupplyStaff.objects.all()
    serializer_class = serializers.SupplyStaffsSerializer

class StudentsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the students
    """
    queryset = pm.Student.objects.all()
    serializer_class = serializers.StudentsSerializer

#class PreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the users' preferences
    """
    #queryset = pm.Preferences.objects.all()
    #serializer_class = serializers.PreferencesSerializer

#class StudentPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the students' preferences
    """
    #queryset = pm.StudentPreferences.objects.all()
    #serializer_class = serializers.StudentPreferencesSerializer

#class GroupPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the groups' preferences
    """
    #queryset = pm.GroupPreferences.objects.all()
    #serializer_class = serializers.GroupPreferencesSerializer

# ------------
# -- GROUPS --
# ------------

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the departments
    """
    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer

class TrainingProgramsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the training programs
    """
    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgramsSerializer

class GroupTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group types
    """
    queryset = bm.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer

class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the groups
    """
    queryset = bm.Group.objects.all()
    serializer_class = serializers.GroupsSerializer

# ------------
# -- TIMING --
# ------------
class DaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the days
    """
    queryset = bm.Day.objects.all()
    serializer_class = serializers.DaysSerializer

class SlotsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the slots
    """
    queryset = bm.Slot.objects.all()
    serializer_class = serializers.SlotsSerializer

class HolidaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the holidays
    """
    queryset = bm.Holiday.objects.all()
    serializer_class = serializers.HolidaysSerializer

class TrainingHalfDaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the half-day trainings
    """
    queryset = bm.TrainingHalfDay.objects.all()
    serializer_class = serializers.TrainingHalfDaysSerializer

class PeriodsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the periods
    """
    queryset = bm.Period.objects.all()
    serializer_class = serializers.PeriodsSerializer

class TimeGeneralSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the settings of time
    """
    queryset = bm.TimeGeneralSettings.objects.all()
    serializer_class = serializers.TimeGeneralSettingsSerializer


# -----------
# -- ROOMS --
# -----------

class RoomTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room types
    """
    queryset = bm.RoomType.objects.all()
    serializer_class = serializers.RoomTypesSerializer

class RoomGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room groups
    """
    queryset = bm.RoomGroup.objects.all()
    serializer_class = serializers.RoomGroupsSerializer

class RoomsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the rooms
    """
    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomsSerializer

class RoomSortsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room sorts
    """
    queryset = bm.RoomSort.objects.all()
    serializer_class = serializers.RoomSortsSerializer

# -------------
# -- COURSES --
# -------------

class ModulesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the modules
    """
    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModulesSerializer

class CourseTypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the course types
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypesSerializer

class CoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the courses
    """
    queryset = bm.Course.objects.all()
    serializer_class = serializers.CoursesSerializer

class ScheduledCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the scheduled courses
    """
    queryset = bm.ScheduledCourse.objects.all()
    serializer_class = serializers.ScheduledCoursesSerializer

# -----------------
# -- PREFERENCES --
# -----------------

class UsersPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the users' preferences
    """
    queryset = bm.UserPreference.objects.all()
    serializer_class = serializers.UsersPreferencesSerializer

class CoursePreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the course preferences
    """
    queryset = bm.CoursePreference.objects.all()
    serializer_class = serializers.CoursePreferencesSerializer

class RoomPreferencesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the room preferences
    """
    queryset = bm.RoomPreference.objects.all()
    serializer_class = serializers.RoomPreferencesSerializer

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the scheduler version
    """
    queryset = bm.EdtVersion.objects.all()
    serializer_class = serializers.EdtVersionSerializer

class CourseModificationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the course modifications
    """
    queryset = bm.CourseModification.objects.all()
    serializer_class = serializers.CourseModificationsSerializer

class PlanningModificationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the planning modifications
    """
    queryset = bm.PlanningModification.objects.all()
    serializer_class = serializers.PlanningModificationsSerializer


# -----------
# -- COSTS --
# -----------

class TutorCostsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the tutor costs
    """
    queryset = bm.TutorCost.objects.all()
    serializer_class = serializers.TutorCostsSerializer

class GroupCostsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group costs
    """
    queryset = bm.GroupCost.objects.all()
    serializer_class = serializers.GroupCostsSerializer

class GroupFreeHalfDaysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the group's free half days
    """
    queryset = bm.GroupFreeHalfDay.objects.all()
    serializer_class = serializers.GroupFreeHalfDaysSerializer


# ----------
# -- MISC --
# ----------

class DependenciesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the dependencies between courses
    """
    queryset = bm.Dependency.objects.all()
    serializer_class = serializers.DependenciesSerializer

class CourseStartTimeConstraintsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the courses start time constraints
    """
    queryset = bm.CourseStartTimeConstraint.objects.all()
    serializer_class = serializers.CourseStartTimeConstraintsSerializer

class RegensViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the regenerations
    """
    queryset = bm.Regen.objects.all()
    serializer_class = serializers.RegensSerializer