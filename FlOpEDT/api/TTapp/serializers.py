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
from TTapp.FlopConstraint import FlopConstraint, all_subclasses
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
    weeks = serializers.SerializerMethodField()
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

        department = obj.department

        if hasattr(obj, "train_progs"):
            train_progs = getattr(obj, "train_progs").values("id")
        else:
            train_progs = []

        for field in obj._meta.get_fields():
            if(field.name not in fields):
                parameters = {}
                id_list = []
                acceptable = []
                allexcept = False
                multiple = False

                if(not field.many_to_one and not field.many_to_many):
                    typename = type(field).__name__

                    #Récupère les validators dans acceptable
                    validators = field.validators
                    if(validators is not empty):
                        for i in validators:
                            acceptable.append(i.limit_value)
                    
                    if(type(field)==ArrayField):
                        multiple = True 
                        typename = type(field.base_field).__name__  
                        #Récupère les choices de l'arrayfield dans acceptable
                        choices = field.base_field.choices
                        if choices is not None:
                            acceptable = choices
                        elif field.name == "possible_start_times":
                            acceptable = all_possible_start_times(department)

                else :
                    #Récupère le modele en relation avec un ManyToManyField ou un ForeignKey
                    mod = field.related_model
                    typenamesplit= str(mod)[8:-2].split(".")
                    typename = typenamesplit[0]+"."+typenamesplit[2]
                    acceptablelist = mod.objects.values("id")

                    #Filtre les ID dans acceptable list en fonction du department
                    if (str(department) != "None"):
                        
                        if(field.name == "tutors"):
                            acceptablelist = acceptablelist.filter(departments=department.id)

                        elif(field.name == "train_progs"):
                            acceptablelist = acceptablelist.filter(department=department.id)
                        
                        elif(field.name == "modules"):
                            acceptablelist = acceptablelist.filter(train_prog__department=department.id)

                        elif(field.name == "groups"):
                            acceptablelist = acceptablelist.filter(train_prog__department=department.id)

                    #Filtre les ID dans acceptable list en fonction des train_progs
                    if (len(train_progs) != 0):
                        if(field.name == "modules"):
                            acceptablelist = acceptablelist.filter(train_prog__in=train_progs)

                        elif(field.name == "groups"):
                            acceptablelist = acceptablelist.filter(train_prog__in=train_progs)

                    #Tout les ID possibles si pas de train_progs ou de department
                    for id in acceptablelist:
                        acceptable.append(id["id"])

                    attr = getattr(obj,field.name)

                    if(field.many_to_one):
                        if( str(attr) != "None"):
                            id_list.append(attr.id)

                    if(field.many_to_many):
                        multiple = True
                        listattr = attr.values("id")
                        for id in listattr:
                            id_list.append(id["id"])

                if( len(id_list)>(len(acceptable)*(3/4)) ):
                    #Permet de récupérer les ID qui ne sont pas selectionné
                    id_list = list(set(acceptable) - set(id_list)) + list(set(id_list) - set(acceptable))
                    allexcept = True    

                parameters["name"] = field.name
                parameters["type"] = typename
                parameters["required"] = not field.blank
                parameters["multiple"] = multiple
                parameters["all_except"] = allexcept
                parameters["id_list"] = id_list
                parameters["acceptable"] = acceptable

                paramlist.append(parameters)

        return(paramlist)

class TTConstraintSerializer(FlopConstraintSerializer):
    class Meta:
        model = ttt.MinTutorsHalfDays
        fields = ['id', 'title', 'name', 'weight', 'is_active', 'comment', "modified_at", 'weeks', 'parameters']

class NoVisioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttv.NoVisio
        fields = '__all__'


class FlopConstraintParametersSerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""
    constraints_parameters = serializers.SerializerMethodField()

    def get_constraints_parameters(self, department):
        result = {}
        paramlist = set()
        for constraint_class in all_subclasses(FlopConstraint):
            fields = constraint_class._meta.get_fields()
            excluded_fields = ['id', 'class_name',
                               'department', 'weight', 'title', 'comment',
                               'is_active', 'modified_at', 'weeks', 'train_progs', 'courses']
            parameters_fields = set([f for f in fields
                                     if f.name not in excluded_fields
                                     and 'IntegerField' not in type(f).__name__])
            paramlist |= parameters_fields
        print(paramlist)


        for field in paramlist:
            acceptable = []

            if (not field.many_to_one and not field.many_to_many):
                typename = type(field).__name__

                # Récupère les validators dans acceptable
                if typename == 'CharField':
                    choices = field.choices
                    if "day" in field.name:
                        acceptable = department.timegeneralsettings.days
                    elif choices is not None:
                        acceptable = [c[0] for c in choices]
                if typename == 'BooleanField':
                    acceptable = [True, False]

                if type(field) is ArrayField:
                    typename = type(field.base_field).__name__
                    # Récupère les choices de l'arrayfield dans acceptable
                    choices = field.base_field.choices
                    if field.name == "possible_start_times":
                        acceptable = all_possible_start_times(department)
                    elif "day" in field.name:
                        acceptable = department.timegeneralsettings.days
                    elif choices is not None:
                        acceptable = choices

            else:
                # Récupère le modele en relation avec un ManyToManyField ou un ForeignKey
                mod = field.related_model
                typenamesplit = str(mod)[8:-2].split(".")
                typename = typenamesplit[0] + "." + typenamesplit[2]
                acceptablelist = mod.objects.values("id")

                # Filtre les ID dans acceptable list en fonction du department
                if (field.name == "tutors"):
                    acceptablelist = acceptablelist.filter(departments=department)

                elif (field.name == "train_progs"):
                    acceptablelist = acceptablelist.filter(department=department)

                elif (field.name == "modules"):
                    acceptablelist = acceptablelist.filter(train_prog__department=department)

                elif (field.name == "groups"):
                    acceptablelist = acceptablelist.filter(train_prog__department=department)

                for element in acceptablelist:
                    acceptable.append(element["id"])

            result[field.name] = {"type": typename,
                                  "acceptable": acceptable}

        return result