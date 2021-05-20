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

import TTapp.models as ttm
import TTapp.TTConstraint as ttc
import TTapp.TTConstraints.tutors_constraints as ttt
import TTapp.TTConstraints.rooms_constraints as ttr
import TTapp.TTConstraints.visio_constraints as ttv
from rest_framework import serializers

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

class TTConstraintSerializer(serializers.ModelSerializer):
    #id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    #weight = serializers.IntegerField()
    #is_active = serializers.BooleanField()
    #comment = serializers.CharField()
    #last_modification = serializers.DateField()
    #week = serializers.IntegerField()
    #year = serializers.IntegerField()
    parameters = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        model = ttc.TTConstraint
        fields = '__all__'
    
    def get_name(self, obj):
        fields = obj._meta.get_fields()
        return(obj.__class__.__name__)

    def get_parameters(self , obj):
        paramlist = []
        for i in obj._meta.get_fields():
            if (i.name not in self.Meta.fields):
                parameters = {}
                id_list = []
                acceptable = []
                acceptablelist = list()
                parameters["name"] = i.name
                
                if(not i.many_to_one and not i.many_to_many):
                    typename = type(i).__name__
                else :
                    typename = i.related_model.__name__
                    mod = i.related_model
                    
                    department = getattr(obj,"department")

                    if(i.name == "tutors"):
                        acceptablelist = list(mod.objects.values("id","departments"))
                        
                        for id in acceptablelist:
                            if(id["departments"] == department.id ) :
                                acceptable.append(id["id"])

                    elif(i.name == "train_progs"):
                        acceptablelist = list(mod.objects.values("id","department"))
                        for id in acceptablelist:
                            if(id["department"] == department.id):
                                acceptable.append(id["id"])

                    else:
                        acceptablelist = list(mod.objects.values("id"))
                        for id in acceptablelist:
                            acceptable.append(id["id"])

                    for id in acceptablelist:
                        acceptable.append(id["id"])

                    if(i.many_to_one):
                        if( str(getattr(obj,i.name)) != "None"):
                            id_list.append(getattr(obj,i.name).id)

                    if(i.many_to_many):
                        idlist = list(getattr(obj,i.name).values("id"))
                        for id in idlist:
                            id_list.append(id["id"])

                parameters["type"] = typename
                parameters["required"] = not i.blank
                parameters["id_list"] = id_list
                parameters["acceptable"] = acceptable
                
                paramlist.append(parameters)

        return(paramlist)

class TTMinTutorsHalfDaysSerializer(TTConstraintSerializer):
    class Meta:
        model = ttt.MinTutorsHalfDays
        fields = ['id', 'name', 'weight', 'is_active', 'comment', 'week', 'year', 'parameters']

class LimitedRoomChoicesSerializer(TTConstraintSerializer):
    class Meta:
        model = ttr.LimitedRoomChoices
        fields = ['id', 'name', 'weight', 'is_active', 'comment', 'week', 'year', 'parameters']

class NoVisioSerializer(TTConstraintSerializer):
    class Meta:
        model = ttv.NoVisio
        fields = ['id', 'name', 'weight', 'is_active', 'comment', 'week', 'year', 'parameters']
