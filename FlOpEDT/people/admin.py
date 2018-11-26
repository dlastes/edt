# -*- coding: utf-8 -*-


from django.contrib import admin
from base.admin import DepartmentModelAdmin

from people.models import FullStaff, SupplyStaff, BIATOS, Tutor

from import_export import resources, fields


class FullStaffAdmin(DepartmentModelAdmin):

    class Meta:
        app_label = 'auth'

class SupplyStaffAdmin(DepartmentModelAdmin):

    class Meta:
        app_label = 'auth'

class BIATOSAdmin(DepartmentModelAdmin):

    class Meta:
        app_label = 'auth'

class TutorResource(resources.ModelResource):

	class Meta:
		model = Tutor
		fields = ( "username", "first_name", "last_name", "email" )
		


admin.site.register(FullStaff, FullStaffAdmin)
admin.site.register(SupplyStaff, SupplyStaffAdmin)
admin.site.register(BIATOS, BIATOSAdmin)
# admin.site.register(Tutor, TutorAdmin)
