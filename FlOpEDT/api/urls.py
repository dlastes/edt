from rest_framework import routers
from api import views

router = routers.SimpleRouter()
router.register(r'departments', views.DepartmentViewSet)

urlpatterns = router.urls