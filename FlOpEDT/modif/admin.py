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

from modif.models import Jour, RoomGroup, Module, Cours, Groupe, Creneau, \
    Disponibilite, Heure, CoursPlace, EdtVersion, CoursModification, \
    PlanifModification, Prof, BreakingNews, TrainingProgramme

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth.models import User

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
                      widget=ForeignKeyWidget(Cours, 'id'))
    no = fields.Field(column_name='num_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Cours, 'no'))
    prof = fields.Field(column_name='prof_nom',
                        attribute='cours__prof__user',
                        widget=ForeignKeyWidget(User, 'username'))
    # prof_first_name = fields.Field(column_name='prof_first_name',
    #                                attribute='cours__prof__user',
    #                                widget=ForeignKeyWidget(User, 'first_name'))
    # prof_last_name = fields.Field(column_name='prof_last_name',
    #                               attribute='cours__prof__user',
    #                               widget=ForeignKeyWidget(User, 'last_name'))
    groupe = fields.Field(column_name='gpe_nom',
                          attribute='cours__groupe',
                          widget=ForeignKeyWidget(Groupe, 'nom'))
    promo = fields.Field(column_name='gpe_promo',
                         attribute='cours__groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    module = fields.Field(column_name='module',
                          attribute='cours__module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    jour = fields.Field(column_name='jour',
                        attribute='creneau__jour',
                        widget=ForeignKeyWidget(Jour, 'no'))
    heure = fields.Field(column_name='heure',
                         attribute='creneau__heure',
                         widget=ForeignKeyWidget(Heure, 'no'))
    # salle = fields.Field(column_name = 'salle',
    #                      attribute = 'salle',
    #                      widget = ForeignKeyWidget(Salle,'nom'))
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(RoomGroup, 'name'))

    class Meta:
        model = CoursPlace
        fields = ('id', 'no', 'groupe', 'promo',
                  'module', 'jour', 'heure', 'semaine', 'room')


class CoursResource(resources.ModelResource):
    promo = fields.Field(column_name='promo',
                         attribute='groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    prof = fields.Field(column_name='prof',
                        attribute='prof__user',
                        widget=ForeignKeyWidget(User, 'username'))
    module = fields.Field(column_name='module',
                          attribute='module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    groupe = fields.Field(column_name='groupe',
                          attribute='groupe',
                          widget=ForeignKeyWidget(Groupe, 'nom'))

    class Meta:
        model = Cours
        fields = ('id', 'no', 'prof', 'groupe', 'promo', 'module')


class SemaineAnResource(resources.ModelResource):
    class Meta:
        model = Cours
        fields = ("semaine", "an")


class DispoResource(resources.ModelResource):
    prof = fields.Field(attribute='prof__user',
                        widget=ForeignKeyWidget(User, 'username'))
    jour = fields.Field(attribute='creneau__jour',
                        widget=ForeignKeyWidget(Jour, 'no'))
    heure = fields.Field(attribute='creneau__heure',
                         widget=ForeignKeyWidget(Heure, 'no'))

    class Meta:
        model = Disponibilite
        fields = ('prof', 'jour', 'heure', 'valeur')


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


class ProfAdmin(admin.ModelAdmin):
    list_display = ('LBD',)
# # from django.utils.text import Truncator
# ordering = ('abbrev',)
#    def abb_name(self,prof):
#        return Truncator(prof.nom).chars(4, truncate='.')
#    abb_name.short_description = 'Aperçu du nom'


class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nature', 'taille', 'surgroupe', 'train_prog')
    ordering = ('taille',)
    list_filter = (('train_prog', DropdownFilterRel),
                   )


# class SalleAdmin(admin.ModelAdmin):
#     list_display = ('nom','tp_ok','td_ok','ce_ok','machine','exam')

class RoomGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ppn', 'abbrev', 'responsable', 'train_prog')
    ordering = ('abbrev',)
    list_filter = (('responsable', DropdownFilterRel),
                   ('train_prog', DropdownFilterRel),)


class CoursAdmin(admin.ModelAdmin):
    list_display = ('module', 'nature', 'groupe', 'prof', 'semaine', 'an')
    ordering = ('an', 'semaine', 'module', 'nature', 'no', 'groupe', 'prof')
    list_filter = (('prof__user', DropdownFilterRel),
                   ('an', DropdownFilterAll),
                   ('semaine', DropdownFilterAll),
                   ('nature', DropdownFilterCho),
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
    list_filter = (('cours__prof__user', DropdownFilterRel),
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
                    'updated_at', 'user')
    list_filter = (('user', DropdownFilterRel),
                   ('cours__an', DropdownFilterAll),
                   ('cours__semaine', DropdownFilterAll),)
    ordering = ('-updated_at', 'an_old', 'semaine_old')


class PlanifMAdmin(admin.ModelAdmin):
    list_display = ('cours', 'semaine_old', 'an_old', 'prof_old', 'updated_at',
                    'user')
    ordering = ('-updated_at', 'an_old', 'semaine_old')
    list_filter = (('user', DropdownFilterRel),
                   ('semaine_old', DropdownFilterAll),
                   ('an_old', DropdownFilterAll),)


class DispoAdmin(admin.ModelAdmin):
    list_display = ('prof', 'creneau', 'valeur', 'semaine', 'an')
    ordering = ('prof', 'an', 'semaine', 'creneau', 'valeur')
    list_filter = (('creneau', DropdownFilterRel),
                   ('semaine', DropdownFilterAll),
                   ('prof', DropdownFilterRel),)


class BreakingNewsAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'x_beg', 'x_end', 'y', 'txt',
                    'fill_color', 'strk_color')
    ordering = ('week', 'year')


# search_fields = ['prof__username']
# @admin.register(Cours)
# class ModuleAggAdmin(admin.ModelAdmin):
#     list_display = ('module','nature','semaine','prof','volh')
#     list_filter = ('module','prof')

#     def volh(self, obj):
#         return obj.volh

#     def get_queryset(self, request):
#         qs = super(ModuleAggAdmin, self).get_queryset(request)
#         print qs
#         return qs.values('nature', 'prof', 'module').annotate(volh=Count('id',
#                                                                distinct=True))

# admin.site.register(Prof, ProfAdmin)
# admin.site.register(Jour, JourAdmin)
# admin.site.register(DemiJour, DemiJourAdmin)
admin.site.register(Groupe, GroupeAdmin)
admin.site.register(RoomGroup, RoomGroupAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Cours, CoursAdmin)
admin.site.register(EdtVersion, EdtVAdmin)
admin.site.register(CoursModification, CoursMAdmin)
admin.site.register(PlanifModification, PlanifMAdmin)
admin.site.register(CoursPlace, CoursPlaceAdmin)
# admin.site.register(CoursLP, CoursLPAdmin)
admin.site.register(Disponibilite, DispoAdmin)
admin.site.register(BreakingNews, BreakingNewsAdmin)
