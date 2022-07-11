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

from django.contrib.postgres.fields.array import ArrayField
from rest_framework.fields import empty
from TTapp.FlopConstraint import FlopConstraint
import TTapp.TTConstraints.tutors_constraints as ttt
import TTapp.TTConstraints.visio_constraints as ttv
from rest_framework import serializers
from base.timing import all_possible_start_times

# ---------------
# ---- TTAPP ----
# ---------------

""" 
class TTCustomConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.CustomConstraint
        fields = '__all__'


class TTLimitCourseTypeTimePerPeriodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.LimitCourseTypeTimePerPeriod
        fields = '__all__'


class TTReasonableDayssSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.ReasonableDays
        fields = '__all__'


class TTStabilizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.Stabilize
        fields = '__all__'


class TTMinHalfDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.MinHalfDays
        fields = '__all__'


class TTMinNonPreferedSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.MinNonPreferedSlot
        fields = '__all__'


class TTAvoidBothTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.AvoidBothTimes
        fields = '__all__'


class TTSimultaneousCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.SimultaneousCourses
        fields = '__all__'


class TTLimitedStartTimeChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.LimitedStartTimeChoices
        fields = '__all__'


class TTLimitedRoomChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttm.LimitedRoomChoices
        fields = '__all__' """

class FlopConstraintSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    #weeks = serializers.SerializerMethodField()
    parameters = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        model = FlopConstraint
        fields = '__all__'

    def get_name(self, obj):
        return(obj.__class__.__name__)

    def get_weeks(self, obj):
        weeklist = []
        weeks = getattr(obj, "weeks").values("nb", "year")

        for i in weeks:
            weeklist.append(i)

        return(weeklist)


    def get_parameters(self, obj):
        paramlist = []

        fields = self.Meta.fields

        for field in obj._meta.get_fields():
            if(field.name not in fields):
                parameters = {}
                id_list = []
                multiple = False

                if(not field.many_to_one and not field.many_to_many):
                    typename = type(field).__name__

                    if(type(field)==ArrayField):
                        multiple = True
                        typename = type(field.base_field).__name__

                else :
                    #Récupère le modele en relation avec un ManyToManyField ou un ForeignKey
                    mod = field.related_model
                    typenamesplit= str(mod)[8:-2].split(".")
                    typename = typenamesplit[0]+"."+typenamesplit[2]
                    attr = getattr(obj,field.name)

                    if(field.many_to_one):
                        if( str(attr) != "None"):
                            id_list.append(attr.id)

                    if(field.many_to_many):
                        multiple = True
                        listattr = attr.values("id")
                        for id in listattr:
                            id_list.append(id["id"])

                parameters["name"] = field.name
                parameters["type"] = typename
                parameters["required"] = not field.blank
                parameters["multiple"] = multiple
                parameters["id_list"] = id_list

                paramlist.append(parameters)

        return(paramlist)


class FlopConstraintTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    local_name = serializers.CharField()
    parameters = serializers.SerializerMethodField()

    def get_parameters(self, obj):
        fields = []
        for field in obj['parameters']:
            multiple = False
            if not (field.many_to_one or field.many_to_many):
                typename = type(field).__name__

                if type(field) == ArrayField:
                    multiple = True
                    typename = type(field.base_field).__name__
            else:
                mod = field.related_model
                typenamesplit = str(mod)[8:-2].split(".")
                typename = typenamesplit[0] + "." + typenamesplit[2]
                if field.many_to_many:
                    multiple = True
            fields.append({'name': field.name, 'type': typename, 'multiple': multiple})
        return fields


class TTConstraintSerializer(FlopConstraintSerializer):
    class Meta:
        model = ttt.MinTutorsHalfDays
        fields = ['id', 'title', 'name', 'weight', 'is_active', 'comment', "modified_at", 'parameters']


class NoVisioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttv.NoVisio
        fields = '__all__'


class FlopConstraintFieldSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    acceptable = serializers.ListField(child=serializers.CharField())
