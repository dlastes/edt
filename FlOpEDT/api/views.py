from rest_framework import viewsets
import django_filters.rest_framework
from api import serializers
import people.models as pm
import base.models as bm
import quote.models as p
import displayweb.models as dwm

# ------------
# -- PEOPLE --
# ------------
class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users
    """
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
class DaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the days
    """
    queryset = bm.Day.objects.all()
    serializer_class = serializers.DaysSerializer
    

class SlotsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the slots
    """
    queryset = bm.Slot.objects.all()
    serializer_class = serializers.SlotsSerializer
    
    filterset_fields = '__all__'
    

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

class ScheduledCoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the scheduled courses
    """
    queryset = bm.ScheduledCourse.objects.all()
    serializer_class = serializers.ScheduledCoursesSerializer
    
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