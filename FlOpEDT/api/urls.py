from rest_framework import routers
from api import views
from django.urls import path
from django.conf.urls import include, url
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer


routerBase = routers.SimpleRouter()
routerPeople = routers.SimpleRouter()
routerDisplayweb = routers.SimpleRouter()
routerTTapp = routers.SimpleRouter()
routerFetch = routers.SimpleRouter()

routerBase.register(r'users', views.UsersViewSet)
routerBase.register(r'userdepartmentsettings', views.UserDepartmentSettingsViewSet)
routerBase.register(r'tutors', views.TutorsViewSet)
routerBase.register(r'supplystaff', views.SupplyStaffsViewSet)
routerBase.register(r'students', views.StudentsViewSet)
#routerBase.register(r'preferences', views.PreferencesViewSet)
#routerBase.register(r'studentspreferences', views.StudentPreferencesViewSet)
#routerBase.register(r'groupspreferences', views.GroupPreferencesViewSet)
routerBase.register(r'departments', views.DepartmentViewSet)
routerBase.register(r'trainingprograms', views.TrainingProgramsViewSet)
routerBase.register(r'grouptypes', views.GroupTypesViewSet)
routerBase.register(r'groups', views.GroupsViewSet)
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

routerPeople.register(r'userspreferences', views.UsersPreferencesViewSet)
routerPeople.register(r'coursepreferences', views.CoursePreferencesViewSet)
routerPeople.register(r'roompreferences', views.RoomPreferencesViewSet)
routerPeople.register(r'edtversions', views.EdtVersionsViewSet)
routerPeople.register(r'coursemodifications', views.CourseModificationsViewSet)
routerPeople.register(r'planningmodifications', views.PlanningModificationsViewSet)
routerPeople.register(r'tutorcosts', views.TutorCostsViewSet)
routerPeople.register(r'groupcosts', views.GroupCostsViewSet)
routerPeople.register(r'groupfreehalfdays', views.GroupFreeHalfDaysViewSet)
routerPeople.register(r'dependencies', views.DependenciesViewSet)
routerPeople.register(r'coursesstarttimeconstraints', views.CourseStartTimeConstraintsViewSet)
routerPeople.register(r'regens', views.RegensViewSet)

routerDisplayweb.register(r'breakingnews', views.BreakingNewsViewSet)
routerDisplayweb.register(r'moduledisplays', views.ModuleDisplaysViewSet)
routerDisplayweb.register(r'trainingprogrammedisplays', views.TrainingProgrammeDisplaysViewSet)
routerDisplayweb.register(r'groupdisplays', views.GroupDisplaysViewSet)


#routerTTapp.register(r'slots', views.TTSlotsViewSet)
# routerTTapp.register(r'constraints', views.TTConstraintsViewSet)
routerTTapp.register(r'customconstrains', views.TTCustomConstraintsViewSet)
routerTTapp.register(r'limitcoursetypetimeperperiods', views.TTLimitCourseTypeTimePerPeriodsViewSet)
routerTTapp.register(r'reasonabledays', views.TTReasonableDaysViewSet)
routerTTapp.register(r'stabilize', views.TTStabilizeViewSet)
routerTTapp.register(r'minhalfdays', views.TTMinHalfDaysViewSet)
routerTTapp.register(r'minnonpreferedslots', views.TTMinNonPreferedSlotsViewSet)
routerTTapp.register(r'avoidbothtimes', views.TTAvoidBothTimesViewSet)
routerTTapp.register(r'simultaneouscourses', views.TTSimultaneousCoursesViewSet)
routerTTapp.register(r'limitedstarttimechoices', views.TTLimitedStartTimeChoicesViewSet) # TODO: Fix
routerTTapp.register(r'limitiedroomchoices', views.TTLimitedRoomChoicesViewSet)

routerFetch.register(r'scheduledcourses', views.ScheduledCoursesViewSet)
routerFetch.register(r'tutorcourses', views.TutorCoursesViewSet)

urlpatterns = [
    path('base/', include(routerBase.urls)),
    path('user/', include(routerPeople.urls)),
    path('displayweb/', include(routerDisplayweb.urls)),
    path('ttapp/', include(routerTTapp.urls)),
    path('fetch/', include(routerFetch.urls)),
]
