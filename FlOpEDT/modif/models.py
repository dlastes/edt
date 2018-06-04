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

from django.contrib.auth.models import User, AbstractUser

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
    x_beg = models.FloatField(default = 2., blank = True)
    x_end = models.FloatField(default = 3., blank = True)
    y = models.PositiveSmallIntegerField(null = True, default = None,
                                         blank = True)
    txt = models.CharField(max_length = 200)
    fill_color = ColorField(default = '#228B22')
    # stroke color
    strk_color = ColorField(default = '#000000')
    
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
    name = models.CharField(max_length = 50)
    abbrev = models.CharField(max_length = 5)

    def __unicode__(self):
        return self.abbrev


class Groupe(models.Model):
    ENTIERE = 'to'
    TD = 'TD'
    TP = 'TP'
    CHOIX_NATURE = ((ENTIERE, 'Classe entière'),
                    (TD, 'Groupe TD'),
                    (TP, 'Groupe TP'))
    nom = models.CharField(max_length = 4)
    train_prog = models.ForeignKey('TrainingProgramme')
    nature = models.CharField(max_length = 2,
                              choices = CHOIX_NATURE,
                              verbose_name = 'Type de classe')
    size = models.PositiveSmallIntegerField()
    basic = models.BooleanField(verbose_name = 'Basic group?', default = False)
    parent_groups = models.ManyToManyField('self',
                                           blank = True,
                                           related_name = "children_groups")

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


class Jour(models.Model):
    no = models.PositiveSmallIntegerField(primary_key = True,
                                          verbose_name = "Numéro")
    nom = models.CharField(max_length=10, verbose_name = "Nom")

    def __str__(self):
        return self.nom[:3]


class Heure(models.Model):
    MATIN = 'AM'
    APREM = 'PM'
    CHOIX_DEMI_JOUR = ((MATIN, 'Matin'), (APREM, 'Après-midi'))
    apm = models.CharField(max_length = 2,
                           choices = CHOIX_DEMI_JOUR,
                           verbose_name = "Demi-journée",
                           default = MATIN)
    no = models.PositiveSmallIntegerField(primary_key=True)
    nom = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


# class Creneau(models.Model):
class Creneau(CachingMixin, models.Model):
    objects = CachingManager()
    jour = models.ForeignKey('Jour')
    heure = models.ForeignKey('Heure')

    def __str__(self):
        return "%s_%s" % (self.jour, self.heure)

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
    name = models.CharField(max_length = 20)
    types = models.ManyToManyField(RoomType,
                                   blank = True,
                                   related_name = "members")

    def __str__(self):
        return self.name


# class Room(models.Model):
class Room(CachingMixin, models.Model):
    objects = CachingManager()
    name = models.CharField(max_length=20)
    subroom_of = models.ManyToManyField(RoomGroup,
                                        blank = True,
                                        related_name = "subrooms")

    def __str__(self):
        return self.name


class RoomPreference(models.Model):
    for_type = models.ForeignKey(RoomType, blank = True, null = True,
                                 related_name = '+')
    prefer = models.ForeignKey(RoomGroup, blank = True, null = True,
                               related_name = '+')
    unprefer = models.ForeignKey(RoomGroup, blank = True, null = True,
                                 related_name = '+')

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
    head = models.ForeignKey('Tutor', null=True, default = None, blank=True)
#    head_name = models.CharField(max_length = 150, null = True, default = None)
    ppn = models.CharField(max_length=5, default='M')
    train_prog = models.ForeignKey('TrainingProgramme')
    nbTD = models.PositiveSmallIntegerField(default=1)
    nbTP = models.PositiveSmallIntegerField(default=1)
    nbCM = models.PositiveSmallIntegerField(default=1)
    nbDS = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.abbrev




# class Cours(models.Model):
class Cours(CachingMixin, models.Model):
    objects = CachingManager()
    CM = 'CM'
    TD = 'TD'
    TP = 'TP'
    DS = 'DS'
    CHOIX_NATURE = ((CM, 'Cours magistral'),
                    (TD, 'Travaux Dirigés'),
                    (TP, 'Travaux Pratiques'),
                    (DS, 'Devoir surveillé'))
    nature = models.CharField(max_length = 2, choices = CHOIX_NATURE)
    room_type = models.ForeignKey('RoomType', null = True)
    no = models.PositiveSmallIntegerField(null = True, blank = True)
    tutor = models.ForeignKey('Tutor',
                              related_name = 'taught_courses',
                              null = True,
                              default = None)
#    tutor_name = models.CharField(max_length = 150,
#                                  null = True,
#                                  default = None)
    supp_tutor = models.ForeignKey('Tutor',
                                   related_name = 'courses_as_supp',
                                   null = True,
                                   default = None,
                                   blank = True)
#    supp_tutor_name = models.CharField(max_length = 150,
#                                       null = True,
#                                       default = None,
#                                       blank = True)
    groupe = models.ForeignKey('Groupe')
    module = models.ForeignKey('Module', related_name = 'module')
    modulesupp = models.ForeignKey('Module', related_name = 'modulesupp',
                                   null = True, blank = True)
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null = True, blank = True)
    an = models.PositiveSmallIntegerField()
    suspens = models.BooleanField(verbose_name = 'En suspens?', default = False)

    def __str__(self):
        return "%s-%s-%s-%s" % \
               (self.module, self.nature, self.tutor_name, self.groupe)


# class CoursPlace(models.Model):
class CoursPlace(CachingMixin, models.Model):
    objects = CachingManager()
    cours = models.ForeignKey('Cours')
    creneau = models.ForeignKey('Creneau')
    room = models.ForeignKey('RoomGroup', blank=True, null=True)
    no = models.PositiveSmallIntegerField(null=True, blank=True)
    noprec = models.BooleanField(
        verbose_name = 'vrai si on ne veut pas garder la salle', default = True)
    copie_travail = models.PositiveSmallIntegerField(default = 0)
    # les utilisateurs auront acces à la copie publique (0)

    def __str__(self):
        return "%s%s:%s-%s" % (self.cours, self.no, self.creneau.id, self.room)

# </editor-fold desc="COURSES">

# <editor-fold desc="PREFERENCES">
# -----------------
# -- PREFERENCES --
# -----------------


class Disponibilite(models.Model):
    #    prof = models.ForeignKey(User)
    tutor = models.ForeignKey('Tutor',
                              null = True,
                              default = None)
#    tutor_name = models.CharField(max_length = 150, null = True, default = None)
    semaine = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null = True)
    an = models.PositiveSmallIntegerField(null = True)
    creneau = models.ForeignKey('Creneau')
    valeur = models.SmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(10)],
        default = 10)

    def __str__(self):
        return "%s-Sem%s: %s=%s" % \
               (self.tutor.username, self.semaine, self.creneau, self.valeur)


class DispoCours(models.Model):
    nature = models.CharField(max_length = 2, choices = Cours.CHOIX_NATURE)
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)],
        null = True)
    an = models.PositiveSmallIntegerField(null = True)
    creneau = models.ForeignKey('Creneau')
    valeur = models.SmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(10)])
    train_prog = models.ForeignKey('TrainingProgramme')

    def __str__(self):
        return "%s=Sem%s:%s-%s=%s" % \
               (self.nature, self.semaine, self.creneau, self.train_prog,
                self.valeur)


class RoomUnavailability(models.Model):
    room = models.ForeignKey('Room')
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    creneau = models.ForeignKey('Creneau')

    def __str__(self):
        return "%s-Sem%s-cren%s" % (self.room, self.semaine, self.creneau.id)


class DemiJourFeriePromo(models.Model):
    apm = models.CharField(max_length = 2, choices = Heure.CHOIX_DEMI_JOUR,
                           verbose_name = "Demi-journée",
                           default = Heure.MATIN)
    jour = models.ForeignKey('Jour')
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    train_prog = models.ForeignKey('TrainingProgramme')


    def __str__(self):
        return "%s-sem %s- %sA" % (self.jour, self.semaine, self.train_prog)

# </editor-fold desc="PREFERENCES">

# <editor-fold desc="MODIFICATIONS">
# -----------------
# - MODIFICATIONS -
# -----------------


class EdtVersion(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    version = models.PositiveIntegerField(default=0)
#    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


# null iff no change
class CoursModification(models.Model):
    cours = models.ForeignKey('Cours')
    semaine_old = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)], null = True)
    an_old = models.PositiveSmallIntegerField(null = True)
    room_old = models.ForeignKey('RoomGroup', blank = True, null = True)
    creneau_old = models.ForeignKey('Creneau', null = True)
    version_old = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now = True)
    initiator = models.ForeignKey('Tutor',
                                  null = True,
                                  default = None)
#    initiator_name = models.CharField(max_length = 150,
#                                      null = True,
#                                      default = None)

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


class PlanifModification(models.Model):
    cours = models.ForeignKey('Cours')
    semaine_old = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)], null = True)
    an_old = models.PositiveSmallIntegerField(null=True)
    tutor_old = models.ForeignKey('Tutor',
                                  related_name = 'impacted_by_planif_modif',
                                  null = True,
                                  default = None)
#    tutor_name_old = models.CharField(max_length = 150,
#                                      null = True,
#                                      default = None)
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey('Tutor',
                                  related_name = 'operated_planif_modif',
                                  null = True,
                                  default = None)
#    initiator_name = models.CharField(max_length = 150,
#                                      null = True,
#                                      default = None)

# </editor-fold desc="MODIFICATIONS">

# <editor-fold desc="COSTS">
# -----------
# -- COSTS --
# -----------


class CoutProf(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    tutor = models.ForeignKey('Tutor',
                              null = True,
                              default = None)
#    tutor_name = models.CharField(max_length = 150,
#                                  null = True,
#                                  default = None)
    valeur = models.FloatField()

    def __str__(self):
        return "sem%s-%s:%s" % (self.semaine, self.tutor.username, self.valeur)


class CoutGroupe(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    groupe = models.ForeignKey('Groupe')
    valeur = models.FloatField()

    def __str__(self):
        return "sem%s-%s:%s" % (self.semaine, self.groupe, self.valeur)


class DJLGroupe(models.Model):
    semaine = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(53)])
    an = models.PositiveSmallIntegerField()
    groupe = models.ForeignKey('Groupe')
    DJL = models.PositiveSmallIntegerField()

    def __str__(self):
        return "sem%s-%s:%s" % (self.semaine, self.groupe, self.DJL)

# </editor-fold desc="COSTS">

# <editor-fold desc="TUTORS">
# ------------
# -- TUTORS --
# ------------


class Tutor(AbstractUser):
    VAC = 'Vac'
    BIATOS = 'BIA'
    FULL_STAFF = 'FuS'
    CHOICE_STATUS = ((VAC, 'Vacataire'),
                    (FULL_STAFF, 'Permanent UT2J (IUT ou non)'),
                    (BIATOS, 'BIATOS'))
    status = models.CharField(max_length = 3,
                              choices = CHOICE_STATUS,
                              default = FULL_STAFF)
    pref_slots_per_day = models.PositiveSmallIntegerField(
        verbose_name = "Combien de créneaux par jour au mieux ?",
        default = 4)
    rights = models.PositiveSmallIntegerField(verbose_name = "Peut forcer ?",
                                              default = 0)
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
        validators = [MinValueValidator(0), MaxValueValidator(4)],
        verbose_name = "Limitation du nombre de jours",
        default = 2)


class FakeUser(models.Model):
    VAC = 'Vac'
    BIATOS = 'BIA'
    FULL_STAFF = 'FuS'
    CHOICE_STATUS = ((VAC, 'Vacataire'),
                    (FULL_STAFF, 'Permanent UT2J (IUT ou non)'),
                    (BIATOS, 'BIATOS'))
    username = models.CharField(max_length = 150)
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 150)
    email = models.EmailField()
    password = models.CharField(max_length = 100)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    is_superuser = models.BooleanField()
    status = models.CharField(max_length = 3,
                              choices = CHOICE_STATUS,
                              default = FULL_STAFF)

    pref_slots_per_day = models.PositiveSmallIntegerField(
        verbose_name = "Combien de créneaux par jour au mieux ?",
        default = 4)
    rights = models.PositiveSmallIntegerField(verbose_name = "Peut forcer ?",
                                              default = 0)
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
        validators = [MinValueValidator(0), MaxValueValidator(4)],
        verbose_name = "Limitation du nombre de jours",
        default = 2)


#class Prof(models.Model):
#    user = models.OneToOneField(User, related_name='proff')
#    VAC = 'Vac'
#    BIATOS = 'BIA'
#    FULL_STAFF = 'FuS'
#    CHOIX_STATUT = ((VAC, 'Vacataire'),
#                    (FULL_STAFF, 'Permanent UT2J (IUT ou non)'),
#                    (BIATOS, 'BIATOS'))
#    pref_slots_per_day = models.PositiveSmallIntegerField(
#        verbose_name = "Combien de créneaux par jour au mieux ?",
#        default = 4)
#    rights = models.PositiveSmallIntegerField(verbose_name = "Peut forcer ?",
#                                              default = 0)
#    statut = models.CharField(max_length = 3,
#                              choices = CHOIX_STATUT, default = FULL_STAFF)
#    # 0b azyx en binaire
#    # x==1 <=> quand "modifier Cours" coché, les cours sont colorés
#    #          avec la dispo du prof
#    # y==1 <=> je peux changer les dispos de tout le monde
#    # FUTUR
#    # z==1 <=> je peux changer les dispos des vacataires d'un module dont
#    #          je suis responsable
#    # a==1 <=> je peux surpasser les contraintes lors de la modification
#    #          de cours
#    LBD = models.PositiveSmallIntegerField(
#        validators = [MinValueValidator(0), MaxValueValidator(4)],
#        verbose_name = "Limitation du nombre de jours",
#        default = 2)
#
#    def __str__(self):
#        return str(self.user.username)


#class FullStaff(Prof):
#    departement = models.CharField(max_length = 50, default = 'INFO')
#    is_iut = models.BooleanField(default = True)
#
#    def __init__(self, *args, **kwargs):
#        super(FullStaff, self).__init__(*args, **kwargs)
#        self.statut = Prof.FULL_STAFF


class FullStaffTmp(models.Model):
    tutor = models.OneToOneField('Tutor')
#    tutor_name = models.CharField(max_length = 150)
    department = models.CharField(max_length = 50, default = 'INFO')
    is_iut = models.BooleanField(default = True)


#class Vacataire(Prof):
#    employer = models.CharField(max_length = 50,
#                                verbose_name = "Employeur ?",
#                                null = True)
#    qualite = models.CharField(max_length = 50, null = True)
#    field = models.CharField(max_length = 50,
#                             verbose_name = "Domaine ?",
#                             null = True)
#
#    def __init__(self, *args, **kwargs):
#        super(Vacataire, self).__init__(*args, **kwargs)
#        self.statut = Prof.VAC

class VacataireTmp(models.Model):
    tutor = models.OneToOneField('Tutor')
#    tutor_name = models.CharField(max_length = 150)
    employer = models.CharField(max_length = 50,
                                verbose_name = "Employeur ?",
                                null = True)
    qualite = models.CharField(max_length = 50, null = True)
    field = models.CharField(max_length = 50,
                             verbose_name = "Domaine ?",
                             null = True)



#class BIATOS(Prof):
#    def __init__(self, *args, **kwargs):
#        super(BIATOS, self).__init__(*args, **kwargs)
#        self.statut = Prof.BIATOS

        # --- Notes sur Prof ---
        #    MinDemiJournees=models.BooleanField(
        #       verbose_name="Min Demi-journées?", default=False)
        #    unparjour=models.BooleanField(verbose_name="Un créneau par jour?",
        #                                  default=False)
        # # (biatos | vacataire) => TPeqTD=false (donc 3h TP <=> 2h TD)
        # # 1h CM <=> 1.5h TD
        # TPeqTD = models.BooleanField()self.periode

class BIATOSTmp(models.Model):
    tutor = models.OneToOneField('Tutor')
#    tutor_name = models.CharField(max_length = 150)

# class Student(models.Model):  # for now: representative
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     group = models.ForeignKey('Groupe')
#
#     def __str__(self):
#         return str(self.user) + u'(G:' + str(self.group) + u')'

# </editor-fold desc="TUTORS">

# <editor-fold desc="DISPLAY">
# -------------
# -- DISPLAY --
# -------------


class ModuleDisplay(models.Model):
    module = models.OneToOneField('Module', related_name = 'display')
    color_bg = models.CharField(max_length = 20, default = "red")
    color_txt = models.CharField(max_length = 20, default = "black")

    def __unicode__(self):
        return unicode(self.module) + u' -> BG: ' + unicode(self.color_bg)\
               + u' ; TXT: ' + unicode(self.color_txt)


class TrainingProgrammeDisplay(models.Model):
    training_programme = models.OneToOneField('TrainingProgramme',
                                              related_name = 'display')
    row = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return unicode(self.training_programme) + u' : Row ' + unicode(self.row)


class GroupDisplay(models.Model):
    group = models.OneToOneField('Groupe',
                                 related_name = 'display')
    button_height = models.PositiveIntegerField(null = True, default = None)
    button_txt = models.CharField(max_length = 20, null = True, default = None)

    def __unicode__(self):
        return unicode(self.group) + u' -> BH: ' + unicode(self.button_height)\
               + u' ; BTXT: ' + unicode(self.button_txt)

# </editor-fold desc="DISPLAY">

# <editor-fold desc="MISC">
# ----------
# -- MISC --
# ----------


class Precede(models.Model):
    cours1 = models.ForeignKey('Cours', related_name='cours1')
    cours2 = models.ForeignKey('Cours', related_name='cours2')
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


# Possible evolutions
# ====================


# from django.contrib.auth.models import AbstractUser
# class User(AbstractUser):
#    abbrev = models.CharField(max_length=3, blank=False)

# need postgresql !
#
# class Dispo(models.Model):
#     prof = models.ForeignKey("Prof")
#     semaine = models.PositiveSmallIntegerField(
#                 validators=[MinValueValidator(0),MaxValueValidator(53)])
#     an = models.PositiveSmallIntegerField()
#     dispo = ArrayField(models.SmallIntegerField(),size=30)


# class ProfU(models.Model):
#     id = models.UUIDField(primary_key=True,
#                           default=uuid.uuid4,
#                           editable=False)
#     user = models.ForeignKey(User, related_name='user',null=True)
#     LBD = models.PositiveSmallIntegerField(
#                      validators=[MinValueValidator(0),MaxValueValidator(4)],
#     verbose_name="Limitation du nombre de jours", default=2)
#     def __str__(self):
#         return self.abbrev
