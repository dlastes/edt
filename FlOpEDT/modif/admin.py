# -*- coding: utf-8 -*-

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

from django.contrib import admin

from modif.models import Day, RoomGroup, Module, Course, Group, Slot, \
    UserPreference, Time, ScheduledCourse, EdtVersion, CourseModification, \
    PlanningModification, BreakingNews, TrainingProgramme, ModuleDisplay, Tutor
# Prof

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, \
    DropdownFilterCho


# from core.models import Book

# class ProfResource(resources.ModelResource):
#
#    class Meta:
#        model = Prof
#        # fields = ('abbrev',)


class CoursPlaceResource(resources.ModelResource):
    id = fields.Field(column_name='id_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Course, 'id'))
    no = fields.Field(column_name='num_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Course, 'no'))
    prof = fields.Field(column_name='prof_nom',
                        attribute='cours__tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    # prof_first_name = fields.Field(column_name='prof_first_name',
    #                                attribute='cours__tutor',
    #                                widget=ForeignKeyWidget(Tutor,
    #                                 'first_name'))
    # prof_last_name = fields.Field(column_name='prof_last_name',
    #                               attribute='cours__tutor',
    #                               widget=ForeignKeyWidget(Tutor, 'last_name'))
    groupe = fields.Field(column_name='gpe_nom',
                          attribute='cours__groupe',
                          widget=ForeignKeyWidget(Group, 'nom'))
    promo = fields.Field(column_name='gpe_promo',
                         attribute='cours__groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    module = fields.Field(column_name='module',
                          attribute='cours__module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    jour = fields.Field(column_name='jour',
                        attribute='creneau__jour',
                        widget=ForeignKeyWidget(Day, 'no'))
    heure = fields.Field(column_name='heure',
                         attribute='creneau__heure',
                         widget=ForeignKeyWidget(Time, 'no'))
    # salle = fields.Field(column_name = 'salle',
    #                      attribute = 'salle',
    #                      widget = ForeignKeyWidget(Salle,'nom'))
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(RoomGroup, 'name'))
    color_bg = fields.Field(column_name='color_bg',
                        attribute='cours__module__display',
                        widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                        attribute='cours__module__display',
                        widget=ForeignKeyWidget(ModuleDisplay, 'color_txt'))

    class Meta:
        model = ScheduledCourse
        fields = ('id', 'no', 'groupe', 'promo', 'color_bg', 'color_txt',
                  'module', 'jour', 'heure', 'semaine', 'room', 'prof')


class CoursResource(resources.ModelResource):
    promo = fields.Field(column_name='promo',
                         attribute='groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    prof = fields.Field(column_name='prof',
                        attribute='tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    module = fields.Field(column_name='module',
                          attribute='module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    groupe = fields.Field(column_name='groupe',
                          attribute='groupe',
                          widget=ForeignKeyWidget(Group, 'nom'))
    color_bg = fields.Field(column_name='color_bg',
                        attribute='module__display',
                        widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                        attribute='module__display',
                        widget=ForeignKeyWidget(ModuleDisplay, 'color_txt'))

    class Meta:
        model = Course
        fields = ('id', 'no', 'tutor_name', 'groupe', 'promo', 'module',
                  'color_bg', 'color_txt', 'prof')


class SemaineAnResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ("semaine", "an")


class DispoResource(resources.ModelResource):
    prof = fields.Field(attribute='user',
                        widget=ForeignKeyWidget(User, 'username'))
    jour = fields.Field(attribute='creneau__jour',
                        widget=ForeignKeyWidget(Day, 'no'))
    heure = fields.Field(attribute='creneau__heure',
                         widget=ForeignKeyWidget(Time, 'no'))

    class Meta:
        model = UserPreference
        fields = ('jour', 'heure', 'valeur', 'prof')


class BreakingNewsResource(resources.ModelResource):
    class Meta:
        model = BreakingNews
        fields = ("x_beg", "x_end", "y", "txt", "fill_color", "strk_color")


# Register your models here.

class JourAdmin(admin.ModelAdmin):
    list_display = ('nom', 'no')
    ordering = ('no',)


# class DemiJourAdmin(admin.ModelAdmin):
#    list_display = ('jour','apm')
#    ordering = ('jour','apm')


class TutorAdmin(admin.ModelAdmin):
    list_display = ('LBD',)
 # # from django.utils.text import Truncator
 # ordering = ('abbrev',)
 #    def abb_name(self,prof):
 #        return Truncator(prof.nom).chars(4, truncate='.')
 #    abb_name.short_description = 'Aperçu du nom'


class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'size', 'train_prog')
    filter_horizontal = ('parent_groups', )
    ordering = ('size',)
    list_filter = (('train_prog', DropdownFilterRel),
                   )


# class SalleAdmin(admin.ModelAdmin):
#     list_display = ('nom','tp_ok','td_ok','ce_ok','machine','exam')

class RoomGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ppn', 'abbrev',
                    'head',
                    'train_prog')
    ordering = ('abbrev',)
    list_filter = (
        ('head', DropdownFilterRel),
        ('train_prog', DropdownFilterRel),)


class CoursAdmin(admin.ModelAdmin):
    list_display = ('module', 'type', 'groupe', 'tutor', 'semaine', 'an')
    ordering = ('an', 'semaine', 'module', 'type', 'no', 'groupe', 'tutor')
    list_filter = (
        ('tutor', DropdownFilterRel),
        ('an', DropdownFilterAll),
        ('semaine', DropdownFilterAll),
        ('type', DropdownFilterRel),
        ('groupe', DropdownFilterAll),
                   )


# class CoursLPAdmin(admin.ModelAdmin):
#     list_display = ('cours','periode')
#     ordering = ('cours__an','cours__semaine','periode')


class CoursPlaceAdmin(admin.ModelAdmin):

    def cours_semaine(o):
        return str(o.cours.semaine)
    cours_semaine.short_description = 'Semaine'
    cours_semaine.admin_order_field = 'cours__semaine'

    def cours_an(o):
        return str(o.cours.an)

    cours_an.short_description = 'Année'
    cours_an.admin_order_field = 'cours__an'
    
    list_display = (cours_semaine, cours_an, 'cours', 'creneau', 'room')
    ordering = ('creneau', 'cours', 'room')
    list_filter = (
        ('cours__tutor', DropdownFilterRel),
        ('cours__an', DropdownFilterAll),
        ('cours__semaine', DropdownFilterAll),)


class EdtVAdmin(admin.ModelAdmin):
    list_display = ('semaine', 'version', 'an')
    ordering = ('an', 'semaine', 'version')
    list_filter = (('semaine', DropdownFilterAll),
                   ('an', DropdownFilterAll)
                   )


class CoursMAdmin(admin.ModelAdmin):
    def cours_semaine(o):
        return str(o.cours.semaine)
    cours_semaine.short_description = 'Semaine'
    cours_semaine.admin_order_field = 'cours__semaine'

    def cours_an(o):
        return str(o.cours.an)

    cours_an.short_description = 'Année'
    cours_an.admin_order_field = 'cours__an'

    list_display = ('cours', cours_semaine, cours_an,
                    'version_old', 'room_old', 'creneau_old',
                    'updated_at', 'initiator'
                    )
    list_filter = (('initiator', DropdownFilterRel),
                   ('cours__an', DropdownFilterAll),
                   ('cours__semaine', DropdownFilterAll),)
    ordering = ('-updated_at', 'an_old', 'semaine_old')


class PlanifMAdmin(admin.ModelAdmin):
    list_display = ('cours', 'semaine_old', 'an_old',
                    'tutor_old',
                    'updated_at',
                    'initiator'
                    )
    ordering = ('-updated_at', 'an_old', 'semaine_old')
    list_filter = (('initiator', DropdownFilterRel),
                   ('semaine_old', DropdownFilterAll),
                   ('an_old', DropdownFilterAll),)


class DispoAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'creneau', 'valeur', 'semaine', 'an')
    ordering = ('tutor', 'an', 'semaine', 'creneau', 'valeur')
    list_filter = (('creneau', DropdownFilterRel),
                   ('semaine', DropdownFilterAll),
                   ('tutor', DropdownFilterRel),
                   )


class BreakingNewsAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'x_beg', 'x_end', 'y', 'txt',
                    'fill_color', 'strk_color')
    ordering = ('week', 'year')


# search_fields = ['prof__username']
# @admin.register(Cours)
# class ModuleAggAdmin(admin.ModelAdmin):
#     list_display = ('module','type','semaine','prof','volh')
#     list_filter = ('module','prof')

#     def volh(self, obj):
#         return obj.volh

#     def get_queryset(self, request):
#         qs = super(ModuleAggAdmin, self).get_queryset(request)
#         print qs
#         return qs.values('type', 'prof', 'module').annotate(volh=Count('id',
#                                                                distinct=True))

admin.site.register(Tutor, TutorAdmin)
# admin.site.register(Jour, JourAdmin)
# admin.site.register(DemiJour, DemiJourAdmin)
admin.site.register(Group, GroupeAdmin)
admin.site.register(RoomGroup, RoomGroupAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Course, CoursAdmin)
admin.site.register(EdtVersion, EdtVAdmin)
admin.site.register(CourseModification, CoursMAdmin)
admin.site.register(PlanningModification, PlanifMAdmin)
admin.site.register(ScheduledCourse, CoursPlaceAdmin)
# admin.site.register(CoursLP, CoursLPAdmin)
admin.site.register(UserPreference, DispoAdmin)
admin.site.register(BreakingNews, BreakingNewsAdmin)
