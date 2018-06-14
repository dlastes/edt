from django.conf.urls import url, include
from .student import AddStudent
from .tutor import AddFullStaffTutor, AddSupplyStaffTutor, AddBIATOSTutor

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls', namespace="auth")),
    url(r'^add-student', AddStudent.as_view(), name="add_student"),
    url(r'^add-fullstaff', AddFullStaffTutor.as_view(), name="add_fullstaff"),
    url(r'^add-supplystaff', AddSupplyStaffTutor.as_view(), name="add_supplystaff"),
    url(r'^add-biatos', AddBIATOSTutor.as_view(), name="add_bi"),
    ]
