# -*- coding: utf-8 -*-


from django.contrib import admin
from base.admin import DepartmentModelAdmin

from people.models import *

from import_export import resources, fields

class TutorModelAdmin(DepartmentModelAdmin):

    def get_department_lookup(self, department):
        """
        Hook for overriding default department lookup research
        """
        return {'departments': department}

    class Meta:
        app_label = 'auth'


class TutorResource(resources.ModelResource):

	class Meta:
		model = Tutor
		fields = ( "username", "first_name", "last_name", "email" )

class StudentPreferencesResource(resources.ModelResource):

    class Meta:
        model = StudentPreferences
        fields = ( "student.username", "student.belong_to", "morning_weight", "free_half_day_weight" )


class GroupPreferencesResource(resources.ModelResource):

    class Meta:
        model = GroupPreferences
        fields = ( "group.name", "morning_weight", "free_half_day_weight" )


admin.site.register(FullStaff, TutorModelAdmin)
admin.site.register(SupplyStaff, TutorModelAdmin)
admin.site.register(BIATOS, TutorModelAdmin)
