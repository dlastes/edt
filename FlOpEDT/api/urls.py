from rest_framework import routers
from api import views
from django.urls import path
from django.conf.urls import include

routerBase = routers.SimpleRouter()
routerPeople = routers.SimpleRouter()

routerPeople.register(r'users', views.UsersViewSet)
routerPeople.register(r'userdepartmentsettings', views.UserDepartmentSettingsViewSet)
routerPeople.register(r'tutors', views.TutorsViewSet)
routerPeople.register(r'supplystaff', views.SupplyStaffsViewSet)
routerPeople.register(r'students', views.StudentsViewSet)
#routerPeople.register(r'preferences', views.PreferencesViewSet)
#routerPeople.register(r'studentspreferences', views.StudentPreferencesViewSet)
#routerPeople.register(r'groupspreferences', views.GroupPreferencesViewSet)


routerBase.register(r'departments', views.DepartmentViewSet)
routerBase.register(r'trainingprograms', views.TrainingProgramsViewSet)
routerBase.register(r'grouptypes', views.GroupTypesViewSet)
routerBase.register(r'grouptypes', views.GroupsViewSet)

routerBase.register(r'days', views.DaysViewSet)
routerBase.register(r'slots', views.SlotsViewSet)
routerBase.register(r'holidays', views.HolidaysViewSet)
routerBase.register(r'traininghalfdays', views.TrainingHalfDaysViewSet)
routerBase.register(r'periods', views.PeriodsViewSet)
routerBase.register(r'timesettings', views.TimeGeneralSettingsViewSet)

routerBase.register(r'roomtypes', views.RoomTypesViewSet)
routerBase.register(r'roomgroups', views.RoomGroupsViewSet)
routerBase.register(r'rooms', views.RoomGroupsViewSet)
routerBase.register(r'roomsorts', views.RoomSortsViewSet)

routerBase.register(r'modules', views.ModulesViewSet)
routerBase.register(r'coursetypes', views.CourseTypesViewSet)
routerBase.register(r'courses', views.CoursesViewSet)
routerBase.register(r'scheduledcourses', views.ScheduledCoursesViewSet)

routerBase.register(r'userspreferences', views.UsersPreferencesViewSet)
routerBase.register(r'coursepreferences', views.CoursePreferencesViewSet)
routerBase.register(r'roompreferences', views.RoomPreferencesViewSet)

routerBase.register(r'edtversions', views.EdtVersionsViewSet)
routerBase.register(r'coursemodifications', views.CourseModificationsViewSet)
routerBase.register(r'planningmodifications', views.PlanningModificationsViewSet)

routerBase.register(r'tutorcosts', views.TutorCostsViewSet)
routerBase.register(r'groupcosts', views.GroupCostsViewSet)
routerBase.register(r'groupfreehalfdays', views.GroupFreeHalfDaysViewSet)

routerBase.register(r'dependencies', views.DependenciesViewSet)
routerBase.register(r'coursesstarttimeconstraints', views.CourseStartTimeConstraintsViewSet)
routerBase.register(r'regens', views.RegensViewSet)

urlpatterns = [
    path('base/', include(routerBase.urls)),
    path('user/', include(routerPeople.urls))
]