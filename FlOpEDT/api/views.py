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
    ViewSet to see all the training programs
    """
    queryset = models.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer