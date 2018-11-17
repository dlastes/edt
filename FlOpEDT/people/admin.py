# -*- coding: utf-8 -*-


from django.contrib import admin
from base.admin import DepartmentModelAdmin

from people.models import FullStaff, SupplyStaff, BIATOS


class FullStaffAdmin(DepartmentModelAdmin):

    class Meta:
        app_label = 'auth'

class SupplyStaffAdmin(DepartmentModelAdmin):

    class Meta:
        app_label = 'auth'

class BIATOSAdmin(DepartmentModelAdmin):

    class Meta:
        app_label = 'auth'


admin.site.register(FullStaff, FullStaffAdmin)
admin.site.register(SupplyStaff, SupplyStaffAdmin)
admin.site.register(BIATOS, BIATOSAdmin)
# admin.site.register(Tutor, TutorAdmin)
