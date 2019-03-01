# -*- coding: utf-8 -*-


from django.contrib import admin
from base.admin import DepartmentModelAdmin
from import_export.widgets import ForeignKeyWidget


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

    student_username = fields.Field(column_name='student_username',
                          attribute='student',
                          widget=ForeignKeyWidget('Student', 'username'))

    student_group = fields.Field(column_name='student_group',
                          attribute='student',
                          widget=ForeignKeyWidget('Student', 'belong_to'))


    class Meta:
        model = StudentPreferences
        fields = ( "student_username", "student_group", "morning_weight", "free_half_day_weight" )


class GroupPreferencesResource(resources.ModelResource):

    train_prog = fields.Field(column_name='train_prog',
                          attribute='group',
                          widget=ForeignKeyWidget('Group', 'train_prog'))

    group = fields.Field(column_name='group_name',
                          attribute='group',
                          widget=ForeignKeyWidget('Group', 'nom'))


    class Meta:
        model = GroupPreferences
        fields = ( "train_prog", "group", "morning_weight", "free_half_day_weight" )


admin.site.register(FullStaff, TutorModelAdmin)
admin.site.register(SupplyStaff, TutorModelAdmin)
admin.site.register(BIATOS, TutorModelAdmin)
