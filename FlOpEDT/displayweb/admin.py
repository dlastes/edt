from django.contrib import admin

from displayweb.models import BreakingNews


class BreakingNewsResource(resources.ModelResource):
    class Meta:
        model = BreakingNews
        fields = ("id", "x_beg", "x_end", "y", "txt", "fill_color", "strk_color", "is_linked")

        
class BreakingNewsAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'x_beg', 'x_end', 'y', 'txt',
                    'fill_color', 'strk_color')
    ordering = ('-year', '-week')

    
admin.site.register(BreakingNews, BreakingNewsAdmin)
