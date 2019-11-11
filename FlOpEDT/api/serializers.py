from rest_framework import serializers
from base import models

# ------------
# -- GROUPS --
# ------------

class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Department
        fields = ['name', 'abbrev']


class TrainingProgramsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TrainingProgramme
        fields = ['name', 'abbrev', 'department']

class GroupTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.GroupType
        fields = ['name', 'department']