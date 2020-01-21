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

from rest_framework import routers
from api import views
from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView
from rest_framework.schemas import get_schema_view
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.views import obtain_auth_token 
# from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from rest_framework_swagger.views import get_swagger_view

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
routerBase.register(r'login', views.LoginView, basename="login")
routerBase.register(r'logout', views.LogoutView, basename="logout")

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

routerFetch.register(r'scheduledcourses', views.ScheduledCoursesViewSet, basename='scheduledcourses')
routerFetch.register(r'unscheduledcourses', views.UnscheduledCoursesViewSet, basename='unscheduledcourses')
routerFetch.register(r'availabilities', views.AvailabilitiesViewSet, basename='availabilities')
routerFetch.register(r'dweek', views.DefaultWeekViewSet)
routerFetch.register(r'coursedefweek', views.CourseDefaultWeekViewSet)
routerFetch.register(r'trainprogs', views.TrainingProgramsViewSet)
routerFetch.register(r'allversions', views.AllVersionsViewSet)
routerFetch.register(r'alltutors', views.AllTutorsViewSet)
routerFetch.register(r'alldepts', views.DepartmentsViewSet)
routerFetch.register(r'tutorcourses', views.TutorCoursesViewSet)
routerFetch.register(r'extrasched', views.ExtraSchedCoursesViewSet)
routerFetch.register(r'bknews', views.BKNewsViewSet)
routerFetch.register(r'coursetypes', views.AllCourseTypesViewSet)


################
# SWAGGER VIEW #
################
swagger_view = get_swagger_view(title='FlOpREST API')


urlpatterns = [
    url(r'^$', views.LoginView.as_view()),
    url(r'^logout/$', views.LogoutView.as_view()),
    url(r'^backoffice/$', login_required(views.TemplateView.as_view(template_name='logout.html'))),
    path('base/', include(routerBase.urls)),
    path('user/', include(routerPeople.urls)),
    path('displayweb/', include(routerDisplayweb.urls)),
    path('ttapp/', include(routerTTapp.urls)),
    path('fetch/', include(routerFetch.urls)),
    path('rest-auth/', include('rest_auth.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    url('doc', swagger_view),
    
]
