# -*- coding: utf-8 -*-


from django.contrib import admin

from people.models import FullStaff, SupplyStaff, BIATOS, Tutor, User

from import_export import resources, fields


class FullStaffAdmin(admin.ModelAdmin):

    class Meta:
        app_label = 'auth'


class SupplyStaffAdmin(admin.ModelAdmin):

    class Meta:
        app_label = 'auth'


class BIATOSAdmin(admin.ModelAdmin):

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
