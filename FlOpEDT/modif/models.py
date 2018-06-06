# coding: utf8
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

from __future__ import unicode_literals

from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models

from django.contrib.auth.models import AbstractUser

from caching.base import CachingManager, CachingMixin

from colorfield.fields import ColorField


# <editor-fold desc="BKNEWS">
# ------------
# -- BKNEWS --
# ------------


class BreakingNews(models.Model):
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    # x_beg and x_end in terms of day width
    x_beg = models.FloatField(default=2., blank=True)
    x_end = models.FloatField(default=3., blank=True)
    y = models.PositiveSmallIntegerField(null=True, default=None,
                                         blank=True)
    txt = models.CharField(max_length=200)
    is_linked = models.URLField(max_length=200, null=True, blank=True, default=None)
    fill_color = ColorField(default='#228B22')
    # stroke color
    strk_color = ColorField(default='#000000')

    def __unicode__(self):
        return u'@(' + unicode(self.x_beg) + u'--' + unicode(self.x_end) \
               + u',' + unicode(self.y) \
               + u')-W' + unicode(self.week) + u',Y' \
               + unicode(self.year) + u': ' + unicode(self.txt)


# </editor-fold>

# <editor-fold desc="GROUPS">
# ------------
# -- GROUPS --
# ------------


class TrainingProgramme(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=5)

    def __unicode__(self):
        return self.abbrev


class GroupType(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Group(models.Model):
    nom = models.CharField(max_length=4)
    train_prog = models.ForeignKey('TrainingProgramme')
    type = models.ForeignKey('GroupType')
    size = models.PositiveSmallIntegerField()
    basic = models.BooleanField(verbose_name='Basic group?', default=False)
    parent_groups = models.ManyToManyField('self',
                                           blank=True,
                                           related_name="children_groups")

    def full_name(self):
        return self.train_prog.abbrev + self.nom

    def __unicode__(self):
        return self.full_name()

    def ancestor_groups(self):
        """
        :return: the set of all Groupe containing self (self not included)
        """
        all = set()
        for gp in self.parent_groups.all():
            all.add(gp)
            for new_gp in gp.ancestor_groups():
                all.add(new_gp)
        return all


# </editor-fold desc="GROUPS">

# <editor-fold desc="TIMING">
# ------------
# -- TIMING --
# ------------


class Day(models.Model):
    no = models.PositiveSmallIntegerField(primary_key=True,
                                          verbose_name="Number")
    nom = models.CharField(max_length=10, verbose_name="Name")

    def __unicode__(self):
        return self.nom[:3]


class Time(models.Model):
    MATIN = 'AM'
    APREM = 'PM'
    CHOIX_DEMI_JOUR = ((MATIN, 'AM'), (APREM, 'PM'))
    apm = models.CharField(max_length=2,
                           choices=CHOIX_DEMI_JOUR,
                           verbose_name="Half day",
                           default=MATIN)
    no = models.PositiveSmallIntegerField(primary_key=True)
    nom = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


# class Creneau(models.Model):
class Slot(CachingMixin, models.Model):
    objects = CachingManager()
    jour = models.ForeignKey('modif.models.Day')
    heure = models.ForeignKey('modif.models.Time')
    duration = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(240)], default=90)

    def __str__(self):
        return "%s_%s" % (self.jour, self.heure)


class Holiday(models.Model):
    apm = models.CharField(max_length=2, choices=Time.CHOIX_DEMI_JOUR,
                           verbose_name="Demi-journée", null=True, default=None, blank=True)
    day = models.ForeignKey('modif.models.Day')
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()


class TrainingHalfDay(models.Model):
    apm = models.CharField(max_length=2, choices=Time.CHOIX_DEMI_JOUR,
                           verbose_name="Demi-journée", null=True, default=None, blank=True)
    day = models.ForeignKey('modif.models.Day')
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
    train_prog = models.ForeignKey('TrainingProgramme', null=True, default=None, blank=True)


class Period(models.Model):
    name = models.CharField(max_length=20)
    starting_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    ending_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
# </editor-fold>

# <editor-fold desc="ROOMS">
# -----------
# -- ROOMS --
# -----------


# class RoomType(models.Model):
class RoomType(CachingMixin, models.Model):
    objects = CachingManager()
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# class RoomGroup(models.Model):
class RoomGroup(CachingMixin, models.Model):
    objects = CachingManager()
    name = models.CharField(max_length=20)
    types = models.ManyToManyField(RoomType,
                                   blank=True,
                                   related_name="members")

    def __str__(self):
        return self.name


# class Room(models.Model):
class Room(CachingMixin, models.Model):
    objects = CachingManager()
    name = models.CharField(max_length=20)
    subroom_of = models.ManyToManyField(RoomGroup,
                                        blank=True,
                                        related_name="subrooms")

    def __str__(self):
        return self.name


class RoomSort(models.Model):
    for_type = models.ForeignKey(RoomType, blank=True, null=True,
                                 related_name='+')
    prefer = models.ForeignKey(RoomGroup, blank=True, null=True,
                               related_name='+')
    unprefer = models.ForeignKey(RoomGroup, blank=True, null=True,
                                 related_name='+')

    def __str__(self):
        return "%s-pref-%s-to-%s" % (self.for_type, self.prefer, self.unprefer)


# </editor-fold>

# <editor-fold desc="COURSES">
# -------------
# -- COURSES --
# -------------


class Module(models.Model):
    nom = models.CharField(max_length=50, null=True)
    abbrev = models.CharField(max_length=10, verbose_name='Intitulé abbrégé')
    head = models.ForeignKey('Tutor',
                             null=True,
                             default=None,
                             blank=True)
    ppn = models.CharField(max_length=5, default='M')
    train_prog = models.ForeignKey('TrainingProgramme')
    period = models.ForeignKey('Period')
    # nbTD = models.PositiveSmallIntegerField(default=1)
    # nbTP = models.PositiveSmallIntegerField(default=1)
    # nbCM = models.PositiveSmallIntegerField(default=1)
    # nbDS = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.abbrev


class CourseType(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


# class Cours(models.Model):
class Course(CachingMixin, models.Model):
    objects = CachingManager()
    type = models.ForeignKey('modif.models.CourseType')
    room_type = models.ForeignKey('RoomType', null=True)
    no = models.PositiveSmallIntegerField(null=True, blank=True)
    tutor = models.ForeignKey('Tutor',
                              related_name='taught_courses',
                              null=True,
                              default=None)
    supp_tutor = models.ManyToManyField('Tutor',
                                        related_name='courses_as_supp',
                                        null=True,
                                        default=None,
                                        blank=True)
    groupe = models.ForeignKey('modif.models.Group')
    module = models.ForeignKey('Module', related_name='module')
    modulesupp = models.ForeignKey('Module', related_name='modulesupp',
                                   null=True, blank=True)
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True, blank=True)
    an = models.PositiveSmallIntegerField()
    suspens = models.BooleanField(verbose_name='En suspens?', default=False)

    def __str__(self):
        return "%s-%s-%s-%s" % \
               (self.module, self.type,
                self.tutor.username if self.tutor is not None else '-no_tut-',
                self.groupe)


# class CoursPlace(models.Model):
class ScheduledCourse(CachingMixin, models.Model):
    objects = CachingManager()
    cours = models.ForeignKey('modif.models.Course')
    creneau = models.ForeignKey('modif.models.Slot')
    room = models.ForeignKey('RoomGroup', blank=True, null=True)
    no = models.PositiveSmallIntegerField(null=True, blank=True)
    noprec = models.BooleanField(
        verbose_name='vrai si on ne veut pas garder la salle', default=True)
    copie_travail = models.PositiveSmallIntegerField(default=0)

    # les utilisateurs auront acces à la copie publique (0)

    def __str__(self):
        return "%s%s:%s-%s" % (self.cours, self.no, self.creneau.id, self.room)


# </editor-fold desc="COURSES">

# <editor-fold desc="PREFERENCES">
# -----------------
# -- PREFERENCES --
# -----------------


class UserPreference(models.Model):
    user = models.ForeignKey('User')
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    an = models.PositiveSmallIntegerField(null=True)
    creneau = models.ForeignKey('modif.models.Slot')
    valeur = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return "%s-Sem%s: %s=%s" % \
               (self.user.username, self.semaine, self.creneau, self.valeur)


class CoursePreference(models.Model):
    course_type = models.ForeignKey('modif.models.CourseType')
    train_prog = models.ForeignKey('TrainingProgramme')
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    an = models.PositiveSmallIntegerField(null=True)
    creneau = models.ForeignKey('modif.models.Slot')
    valeur = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return "%s=Sem%s:%s-%s=%s" % \
               (self.nature, self.semaine, self.creneau, self.train_prog,
                self.valeur)


class RoomPreference(models.Model):
    room = models.ForeignKey('Room')
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    an = models.PositiveSmallIntegerField(null=True)
    creneau = models.ForeignKey('modif.models.Slot')
    valeur = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return "%s-Sem%s-cren%s=%s" % (self.room, self.semaine, self.creneau.id, self.valeur)


# </editor-fold desc="PREFERENCES">

# <editor-fold desc="MODIFICATIONS">
# -----------------
# - MODIFICATIONS -
# -----------------


class EdtVersion(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    version = models.PositiveIntegerField(default=0)


#    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


# null iff no change
class CourseModification(models.Model):
    cours = models.ForeignKey('modif.models.Course')
    semaine_old = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    an_old = models.PositiveSmallIntegerField(null=True)
    room_old = models.ForeignKey('RoomGroup', blank=True, null=True)
    creneau_old = models.ForeignKey('modif.models.Slot', null=True)
    version_old = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey('Tutor')

    def __str__(self):
        olds = 'OLD:'
        if self.semaine_old:
            olds += u' Sem ' + str(self.semaine_old) + u' ;'
        if self.an_old:
            olds += u' An ' + str(self.an_old) + u' ;'
        if self.room_old:
            olds += u' Salle ' + str(self.room_old) + u' ;'
        if self.creneau_old:
            olds += u' Cren ' + str(self.creneau_old) + u' ;'
        if self.version_old:
            olds += u' NumV ' + str(self.version_old) + u' ;'
        return "by %s, at %s\n%s <- %s" % (self.initiator.username,
                                           self.updated_at,
                                           self.cours,
                                           olds)


class PlanningModification(models.Model):
    cours = models.ForeignKey('modif.models.Course')
    semaine_old = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    an_old = models.PositiveSmallIntegerField(null=True)
    tutor_old = models.ForeignKey('Tutor',
                                  related_name='impacted_by_planif_modif',
                                  null=True,
                                  default=None)
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey('Tutor',
                                  related_name='operated_planif_modif')


# </editor-fold desc="MODIFICATIONS">

# <editor-fold desc="COSTS">
# -----------
# -- COSTS --
# -----------


class TutorCost(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    tutor = models.ForeignKey('Tutor')
    valeur = models.FloatField()

    def __str__(self):
        return "sem%s-%s:%s" % (self.semaine, self.tutor.username, self.valeur)


class GroupCost(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    groupe = models.ForeignKey('modif.models.Group')
    valeur = models.FloatField()

    def __str__(self):
        return "sem%s-%s:%s" % (self.semaine, self.groupe, self.valeur)


class GroupFreeHalfDay(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    groupe = models.ForeignKey('modif.models.Group')
    DJL = models.PositiveSmallIntegerField()

    def __str__(self):
        return "sem%s-%s:%s" % (self.semaine, self.groupe, self.DJL)


# </editor-fold desc="COSTS">

# <editor-fold desc="TUTORS">
# ------------
# -- TUTORS --
# ------------


class User(AbstractUser):
    pass


class Tutor(User):
    pref_slots_per_day = models.PositiveSmallIntegerField(
        verbose_name="How many slots per day would you prefer ?",
        default=4)
    rights = models.PositiveSmallIntegerField(verbose_name="Peut forcer ?",
                                              default=0)
    # 0b azyx en binaire
    # x==1 <=> quand "modifier Cours" coché, les cours sont colorés
    #          avec la dispo du prof
    # y==1 <=> je peux changer les dispos de tout le monde
    # FUTUR
    # z==1 <=> je peux changer les dispos des vacataires d'un module dont
    #          je suis responsable
    # a==1 <=> je peux surpasser les contraintes lors de la modification
    #          de cours
    LBD = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        verbose_name="Limitation du nombre de jours",
        default=2)


class FullStaff(models.Model):
    tutor = models.OneToOneField('Tutor')
    department = models.CharField(max_length=50, default='INFO')
    is_iut = models.BooleanField(default=True)


#    def __init__(self, *args, **kwargs):
#        super(FullStaff, self).__init__(*args, **kwargs)
#        self.statut = Prof.FULL_STAFF


class SupplyStaff(models.Model):
    tutor = models.OneToOneField('Tutor')
    employer = models.CharField(max_length=50,
                                verbose_name="Employeur ?",
                                null=True)
    qualite = models.CharField(max_length=50, null=True)
    field = models.CharField(max_length=50,
                             verbose_name="Domaine ?",
                             null=True)


class BIATOS(models.Model):
    tutor = models.OneToOneField('Tutor')


# --- Notes sur Prof ---
#    MinDemiJournees=models.BooleanField(
#       verbose_name="Min Demi-journées?", default=False)
#    unparjour=models.BooleanField(verbose_name="Un créneau par jour?",
#                                  default=False)
# # (biatos | vacataire) => TPeqTD=false (donc 3h TP <=> 2h TD)
# # 1h CM <=> 1.5h TD
# TPeqTD = models.BooleanField()self.periode


class Student(User):  # for now: representative
    group = models.ForeignKey('Groupe')

    def __str__(self):
        return str(self.username) + u'(G:' + str(self.group) + u')'


# </editor-fold desc="TUTORS">

# <editor-fold desc="DISPLAY">
# -------------
# -- DISPLAY --
# -------------


class ModuleDisplay(models.Model):
    module = models.OneToOneField('Module', related_name='display')
    color_bg = models.CharField(max_length=20, default="red")
    color_txt = models.CharField(max_length=20, default="black")

    def __unicode__(self):
        return unicode(self.module) + u' -> BG: ' + unicode(self.color_bg) \
               + u' ; TXT: ' + unicode(self.color_txt)


class TrainingProgrammeDisplay(models.Model):
    training_programme = models.OneToOneField('TrainingProgramme',
                                              related_name='display')
    row = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return unicode(self.training_programme) + u' : Row ' + unicode(self.row)


class GroupDisplay(models.Model):
    group = models.OneToOneField('modif.models.Group',
                                 related_name='display')
    button_height = models.PositiveIntegerField(null=True, default=None)
    button_txt = models.CharField(max_length=20, null=True, default=None)

    def __unicode__(self):
        return unicode(self.group) + u' -> BH: ' + unicode(self.button_height) \
               + u' ; BTXT: ' + unicode(self.button_txt)


# </editor-fold desc="DISPLAY">

# <editor-fold desc="MISC">
# ----------
# -- MISC --
# ----------


class Dependency(models.Model):
    cours1 = models.ForeignKey('modif.models.Course', related_name='cours1')
    cours2 = models.ForeignKey('modif.models.Course', related_name='cours2')
    successifs = models.BooleanField(verbose_name='Successifs?', default=False)
    ND = models.BooleanField(verbose_name='Jours differents', default=False)

    def __str__(self):
        return "%s avant %s" % (self.cours1, self.cours2)


class Regen(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    full = models.BooleanField(verbose_name='Complète',
                               default=True)
    fday = models.PositiveSmallIntegerField(verbose_name='Jour',
                                            default=1)
    fmonth = models.PositiveSmallIntegerField(verbose_name='Mois',
                                              default=1)
    fyear = models.PositiveSmallIntegerField(verbose_name='Année',
                                             default=1)
    stabilize = models.BooleanField(verbose_name='Stabilisée',
                                    default=False)
    sday = models.PositiveSmallIntegerField(verbose_name='Jour',
                                            default=1)
    smonth = models.PositiveSmallIntegerField(verbose_name='Mois',
                                              default=1)
    syear = models.PositiveSmallIntegerField(verbose_name='Année',
                                             default=1)

    def __str__(self):
        pre = ''
        if self.full:
            pre = u'C,' + str(self.fday) + u"/" + str(self.fmonth) \
                  + u"/" + str(self.fyear) + u" "
        if self.stabilize:
            pre = u'S,' + str(self.sday) + u"/" + str(self.smonth) \
                  + u"/" + str(self.syear)
        if not self.full and not self.stabilize:
            pre = u'N'
        return pre

    def strplus(self):
        ret = u"Semaine " + str(self.semaine).encode('utf8') \
              + u" (" + str(self.an).encode('utf8') + u") : "
        # ret.encode('utf8')

        if self.full:
            ret += u'Génération complète le ' + self.fday.encode('utf8') \
                   + u"/" + str(self.fmonth) + u"/" + str(self.fyear)
        elif self.stabilize:
            ret += u'Génération stabilisée le ' + str(self.sday) + u"/" \
                   + str(self.smonth) + u"/" + str(self.syear)
        else:
            ret += u"Pas de (re-)génération prévue"

        return ret

# </editor-fold desc="MISC">
# </editor-fold desc="MISC">
