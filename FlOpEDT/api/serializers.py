from rest_framework import serializers
from base import models

class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Department
        fields = ['name', 'abbrev']