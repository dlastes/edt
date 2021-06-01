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

from base.models import Week
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
    name = serializers.SerializerMethodField()
    weeks = serializers.SerializerMethodField()
    parameters = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        model = ttc.TTConstraint
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
        department = obj.department

        for field in obj._meta.get_fields():
            if(field.name not in fields):
                parameters = {}
                id_list = []
                acceptable = []
                acceptablelist = list()

                if(not field.many_to_one and not field.many_to_many):
                    typename = type(field).__name__
                else :
                    typename = str(field.related_model)[8:-2] 
                    mod = field.related_model
                    
                    if(field.name == "tutors" and str(department) != "None"):
                        acceptablelist = mod.objects.values("id","departments").filter(departments=department.id)

                    elif(field.name == "train_progs" and str(department) != "None"):
                        acceptablelist = mod.objects.values("id","department").filter(department=department.id)

                    else:
                        acceptablelist = mod.objects.values("id")

                    for id in acceptablelist:
                        acceptable.append(id["id"])

                    attr = getattr(obj,field.name)

                    if(field.many_to_one):
                        if( str(attr) != "None"):
                            id_list.append(attr.id)

                    if(field.many_to_many):
                        listattr = attr.values("id")
                        for id in listattr:
                            id_list.append(id["id"])

                parameters["name"] = field.name
                parameters["type"] = typename
                parameters["required"] = not field.blank
                parameters["id_list"] = id_list
                parameters["acceptable"] = acceptable

                paramlist.append(parameters)

        return(paramlist)

class TTMinTutorsHalfDaysSerializer(TTConstraintSerializer):
    class Meta:
        model = ttt.MinTutorsHalfDays
        fields = ['id', 'name', 'weight', 'is_active', 'comment', "modified_at", 'weeks', 'parameters']

class LimitedRoomChoicesSerializer(TTConstraintSerializer):
    class Meta:
        model = ttr.LimitedRoomChoices
        fields = ['id', 'name', 'weight', 'is_active', 'comment', "modified_at", 'weeks', 'parameters']

