from rest_framework import viewsets
from api import serializers
from base import models

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the departments
    """
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer