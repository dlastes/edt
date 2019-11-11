from rest_framework import routers
from api import views

router = routers.SimpleRouter()

router.register(r'users', views.UsersViewSet)
router.register(r'userdepartmentsettings', views.UserDepartmentSettingsViewSet)
router.register(r'tutors', views.TutorsViewSet)
router.register(r'supplystaff', views.SupplyStaffsViewSet)
router.register(r'students', views.StudentsViewSet)
#router.register(r'preferences', views.PreferencesViewSet)
#router.register(r'studentspreferences', views.StudentPreferencesViewSet)
#router.register(r'groupspreferences', views.GroupPreferencesViewSet)


router.register(r'departments', views.DepartmentViewSet)
router.register(r'trainingprograms', views.TrainingProgramsViewSet)
router.register(r'grouptypes', views.GroupTypesViewSet)
router.register(r'grouptypes', views.GroupsViewSet)

router.register(r'days', views.DaysViewSet)
router.register(r'slots', views.SlotsViewSet)
router.register(r'holidays', views.HolidaysViewSet)
router.register(r'traininghalfdays', views.TrainingHalfDaysViewSet)
router.register(r'periods', views.PeriodsViewSet)
router.register(r'timesettings', views.TimeGeneralSettingsViewSet)

router.register(r'roomtypes', views.RoomTypesViewSet)
router.register(r'roomgroups', views.RoomGroupsViewSet)
router.register(r'rooms', views.RoomGroupsViewSet)
router.register(r'roomsorts', views.RoomSortsViewSet)

router.register(r'modules', views.ModulesViewSet)
router.register(r'coursetypes', views.CourseTypesViewSet)
router.register(r'courses', views.CoursesViewSet)
router.register(r'scheduledcourses', views.ScheduledCoursesViewSet)

router.register(r'userspreferences', views.UsersPreferencesViewSet)
router.register(r'coursepreferences', views.CoursePreferencesViewSet)
router.register(r'roompreferences', views.RoomPreferencesViewSet)

router.register(r'edtversions', views.EdtVersionsViewSet)
router.register(r'coursemodifications', views.CourseModificationsViewSet)
router.register(r'planningmodifications', views.PlanningModificationsViewSet)

router.register(r'tutorcosts', views.TutorCostsViewSet)
router.register(r'groupcosts', views.GroupCostsViewSet)
router.register(r'groupfreehalfdays', views.GroupFreeHalfDaysViewSet)

router.register(r'dependencies', views.DependenciesViewSet)
router.register(r'coursesstarttimeconstraints', views.CourseStartTimeConstraintsViewSet)
router.register(r'regens', views.RegensViewSet)

urlpatterns = router.urls