# -*- coding: utf-8 -*-


from django.contrib import admin

from people.models import FullStaff, SupplyStaff, BIATOS, Tutor, User


class FullStaffAdmin(admin.ModelAdmin):

    class Meta:
        app_label = 'auth'


class SupplyStaffAdmin(admin.ModelAdmin):

    class Meta:
        app_label = 'auth'


class BIATOSAdmin(admin.ModelAdmin):

    class Meta:
        app_label = 'auth'



admin.site.register(FullStaff, FullStaffAdmin)
admin.site.register(SupplyStaff, SupplyStaffAdmin)
admin.site.register(BIATOS, BIATOSAdmin)
# admin.site.register(Tutor, TutorAdmin)
