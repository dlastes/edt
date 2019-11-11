from rest_framework import routers
from api import views

router = routers.SimpleRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'trainingprograms', views.TrainingProgramsViewSet)
router.register(r'grouptypes', views.GroupTypesViewSet)

urlpatterns = router.urls