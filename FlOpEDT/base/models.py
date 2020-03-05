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

from colorfield.fields import ColorField

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from base.timing import hr_min, str_slot

# <editor-fold desc="GROUPS">
# ------------
# -- GROUPS --
# ------------

class Department(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=7)

    def __str__(self):
        return self.abbrev


class TrainingProgramme(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=5)
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.abbrev


class GroupType(models.Model):
    name = models.CharField(max_length=50)
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=10)
    train_prog = models.ForeignKey('TrainingProgramme', on_delete=models.CASCADE)
    type = models.ForeignKey('GroupType', on_delete=models.CASCADE)
    size = models.PositiveSmallIntegerField()
    basic = models.BooleanField(verbose_name='Basic group?', default=False)
    parent_groups = models.ManyToManyField('self', symmetrical=False,
                                           blank=True,
                                           related_name="children_groups")

    def full_name(self):
        return self.train_prog.abbrev + "-" + self.name

    def __str__(self):
        return self.name

    def ancestor_groups(self):
        """
        :return: the set of all Groupe containing self (self not included)
        """
        ancestors = set(self.parent_groups.all())

        for gp in self.parent_groups.all():

            for new_gp in gp.ancestor_groups():
                ancestors.add(new_gp)

        return ancestors

    def descendants_groups(self):
        """
        :return: the set of all Groupe contained by self (self not included)
        """
        descendants = set()

        for gp in Group.objects.filter(train_prog=self.train_prog):
            if self in gp.ancestor_groups():
                descendants.add(gp)

        return descendants


# </editor-fold desc="GROUPS">


# <editor-fold desc="TIMING">
# ------------
# -- TIMING --
# ------------

class Day(object):
    MONDAY = "m"
    TUESDAY = "tu"
    WEDNESDAY = "w"
    THURSDAY = "th"
    FRIDAY = "f"
    SATURDAY = "sa"
    SUNDAY = "su"

    CHOICES = ((MONDAY, "monday"), (TUESDAY, "tuesday"),
               (WEDNESDAY, "wednesday"), (THURSDAY, "thursday"),
               (FRIDAY, "friday"),(SATURDAY, "saturday"),
               (SUNDAY,"sunday"))

    def __init__(self, day, week):
        self.day = day
        self.week = week

    def __str__(self):
        # return self.nom[:3]
        return self.day + '_s' + str(self.week)


# will not be used
# TO BE DELETED at the end
class Time(models.Model):
    AM = 'AM'
    PM = 'PM'
    HALF_DAY_CHOICES = ((AM, 'AM'), (PM, 'PM'))
    apm = models.CharField(max_length=2,
                           choices=HALF_DAY_CHOICES,
                           verbose_name="Half day",
                           default=AM)
    no = models.PositiveSmallIntegerField(default=0)
    #nom = models.CharField(max_length=20)
    hours = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(25)], default=8)
    minutes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(59)], default=0)

    def __str__(self):
        return str(self.hours)

    def full_name(self):
        message = str(self.hours) + ":"
        if self.minutes < 10:
            message += "0"
        message += str(self.minutes)
        return message

@receiver(pre_save, sender=Time)
def define_apm(sender, instance, *args, **kwargs):
    if instance.hours >= 12:
        instance.apm = Time.PM


class Holiday(models.Model):
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()


class TrainingHalfDay(models.Model):
    apm = models.CharField(max_length=2, choices=Time.HALF_DAY_CHOICES,
                           verbose_name="Demi-journée", null=True, default=None, blank=True)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
    train_prog = models.ForeignKey('TrainingProgramme', null=True, default=None, blank=True, on_delete=models.CASCADE)


class Period(models.Model):
    name = models.CharField(max_length=20)
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    starting_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    ending_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])

    def __str__(self):
        return f"Period {self.name}: {self.department}, {self.starting_week} -> {self.ending_week}"


class TimeGeneralSettings(models.Model):
    department =  models.OneToOneField(Department, on_delete=models.CASCADE)
    day_start_time = models.PositiveSmallIntegerField()
    day_finish_time = models.PositiveSmallIntegerField()
    lunch_break_start_time = models.PositiveSmallIntegerField()
    lunch_break_finish_time = models.PositiveSmallIntegerField()
    days = ArrayField(models.CharField(max_length=2,
                                       choices=Day.CHOICES))
    default_preference_duration = models.PositiveSmallIntegerField(default=90)

    def __str__(self):
        dsh, dsm = hr_min(self.day_start_time)
        lsh, lsm = hr_min(self.lunch_break_start_time)
        dfh, dfm = hr_min(self.day_finish_time)
        lfh, lfm = hr_min(self.lunch_break_finish_time)
        return f"Dept {self.department.abbrev}: " + \
            f"{dsh}:{dsm:02d} - {lsh}:{lsm:02d}" + \
            f" | {lfh}:{lfm:02d} - {dfh}:{dfm:02d};" + \
            f" Days: {self.days}"

# </editor-fold>

# <editor-fold desc="ROOMS">
# -----------
# -- ROOMS --
# -----------


class RoomType(models.Model):
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class RoomGroup(models.Model):
    name = models.CharField(max_length=20)
    types = models.ManyToManyField(RoomType,
                                   blank=True,
                                   related_name="members")

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=20)
    subroom_of = models.ManyToManyField(RoomGroup,
                                        blank=True,
                                        related_name="subrooms")
    departments = models.ManyToManyField(Department)

    def __str__(self):
        return self.name


class RoomSort(models.Model):
    for_type = models.ForeignKey(RoomType, blank=True, null=True,
                                 related_name='+', on_delete=models.CASCADE)
    prefer = models.ForeignKey(RoomGroup, blank=True, null=True,
                               related_name='+', on_delete=models.CASCADE)
    unprefer = models.ForeignKey(RoomGroup, blank=True, null=True,
                                 related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return "{self.for_type}-pref-{self.prefer}-to-{self.unprefer}"


# </editor-fold>

# <editor-fold desc="COURSES">
# -------------
# -- COURSES --
# -------------


class Module(models.Model):
    name = models.CharField(max_length=100, null=True)
    abbrev = models.CharField(max_length=10, verbose_name='Intitulé abbrégé')
    head = models.ForeignKey('people.Tutor',
                             null=True,
                             default=None,
                             blank=True,
                             on_delete=models.CASCADE)
    ppn = models.CharField(max_length=8, default='M')
    train_prog = models.ForeignKey('TrainingProgramme', on_delete=models.CASCADE)
    period = models.ForeignKey('Period', on_delete=models.CASCADE)

    def __str__(self):
        return self.abbrev

    class Meta:
       ordering = ['abbrev',]


class ModulePossibleTutors(models.Model):
    module = models.OneToOneField('Module', on_delete=models.CASCADE)
    possible_tutors = models.ManyToManyField('people.Tutor', blank=True, related_name='possible_modules')


class CourseType(models.Model):
    name = models.CharField(max_length=50)
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    duration = models.PositiveSmallIntegerField(default=90)
    group_types = models.ManyToManyField(GroupType,
                                         blank=True,
                                         related_name="compatible_course_types")

    def __str__(self):
        return self.name


class Course(models.Model):
    type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    room_type = models.ForeignKey('RoomType', null=True, on_delete=models.CASCADE)
    no = models.PositiveSmallIntegerField(null=True, blank=True)
    tutor = models.ForeignKey('people.Tutor',
                              related_name='taught_courses',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    supp_tutor = models.ManyToManyField('people.Tutor',
                                        related_name='courses_as_supp',
                                        blank=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', related_name='module', on_delete=models.CASCADE)
    modulesupp = models.ForeignKey('Module', related_name='modulesupp',
                                   null=True, blank=True, on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    suspens = models.BooleanField(verbose_name='En suspens?', default=False)

    def __str__(self):
        username_mod = self.tutor.username if self.tutor is not None else '-no_tut-'
        return f"{self.type}-{self.module}-{username_mod}-{self.group}"

    def full_name(self):
        username_mod = self.tutor.username if self.tutor is not None else '-no_tut-'
        return f"{self.type}-{self.module}-{username_mod}-{self.group}"

    def get_tutor(self):
        return self.tutor

    def get_group(self):
        return self.group

    def get_module(self):
        return self.module

class CoursePossibleTutors(models.Model):
    course = models.OneToOneField('Course', on_delete=models.CASCADE)
    possible_tutors = models.ManyToManyField('people.Tutor', blank=True, related_name='shared_possible_courses')


class ScheduledCourse(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    # in minutes from 12AM
    start_time = models.PositiveSmallIntegerField()
    room = models.ForeignKey('RoomGroup', blank=True, null=True, on_delete=models.CASCADE)
    no = models.PositiveSmallIntegerField(null=True, blank=True)
    noprec = models.BooleanField(
        verbose_name='vrai si on ne veut pas garder la salle', default=True)
    work_copy = models.PositiveSmallIntegerField(default=0)
    tutor = models.ForeignKey('people.Tutor',
                              related_name='taught_scheduled_courses',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    # les utilisateurs auront acces à la copie publique (0)

    def __str__(self):
        return f"{self.course}{self.no}:{self.day}-t{self.start_time}-{self.room}"

    def end_time(self):
        return self.start_time + self.course.type.duration


# </editor-fold desc="COURSES">

# <editor-fold desc="PREFERENCES">
# -----------------
# -- PREFERENCES --
# -----------------


class UserPreference(models.Model):
    user = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    year = models.PositiveSmallIntegerField(null=True)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    start_time = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField()
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return f"{self.user.username}-Sem{self.week}: " + \
            f"({str_slot(self.day, self.start_time, self.duration)})" + \
            f"={self.value}"


class CoursePreference(models.Model):
    course_type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    train_prog = models.ForeignKey('TrainingProgramme', on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True,
        blank=True)
    year = models.PositiveSmallIntegerField(null=True,
                                          blank=True)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    start_time = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField()
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return f"{self.course_type}=Sem{self.week}:" + \
            f"({str_slot(self.day, self.start_time, self.duration)})" + \
            f"--{self.train_prog}={self.value}"


class RoomPreference(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True,
        blank=True)
    year = models.PositiveSmallIntegerField(null=True,
                                          blank=True)
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    start_time = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField()
    value = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(8)],
        default=8)

    def __str__(self):
        return f"{self.room}-Sem{self.week}:" + \
            f"({str_slot(self.day, self.start_time, self.duration)})" + \
            f"={self.value}"


# </editor-fold desc="PREFERENCES">

# <editor-fold desc="MODIFICATIONS">
# -----------------
# - MODIFICATIONS -
# -----------------


class EdtVersion(models.Model):
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
    version = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("department","week","year"),)
#    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


# null iff no change
class CourseModification(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    old_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    old_year = models.PositiveSmallIntegerField(null=True)
    room_old = models.ForeignKey('RoomGroup', blank=True, null=True, on_delete=models.CASCADE)
    day_old = models.CharField(max_length=2, choices=Day.CHOICES, default=None, null=True)
    start_time_old = models.PositiveSmallIntegerField(default=None, null=True)
    version_old = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)

    def __str__(self):
        olds = 'OLD:'
        if self.old_week is not None:
            olds += f' Sem {self.old_week} ;'
        if self.old_year is not None:
            olds += f' An {self.old_year} ;'
        if self.room_old is not None:
            olds += f' Salle {self.room_old} ;'
        if self.day_old is not None:
            olds += f' Cren {self.day_old}-{self.start_time_old} ;'
        if self.version_old is not None:
            olds += f' NumV {self.version_old} ;'
        return f"by {self.initiator.username}, at {self.updated_at}\n" + \
            f"{self.course} <- {olds}"


class PlanningModification(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    old_week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)], null=True)
    old_year = models.PositiveSmallIntegerField(null=True)
    tutor_old = models.ForeignKey('people.Tutor',
                                  related_name='impacted_by_planif_modif',
                                  null=True,
                                  default=None,
                                  on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    initiator = models.ForeignKey('people.Tutor',
                                  related_name='operated_planif_modif',
                                  on_delete=models.CASCADE)


# </editor-fold desc="MODIFICATIONS">

# <editor-fold desc="COSTS">
# -----------
# -- COSTS --
# -----------


class TutorCost(models.Model):
    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    value = models.FloatField()
    work_copy = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"sem{self.week}-{self.tutor.username}:{self.value}"


class GroupCost(models.Model):
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    value = models.FloatField()
    work_copy = models.PositiveSmallIntegerField(default=0)


    def __str__(self):
        return f"sem{self.week}-{self.group}:{self.value}"


class GroupFreeHalfDay(models.Model):
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    DJL = models.PositiveSmallIntegerField()
    work_copy = models.PositiveSmallIntegerField(default=0)


    def __str__(self):
        return f"sem{self.week}-{self.group}:{self.DJL}"


# </editor-fold desc="COSTS">


# <editor-fold desc="MISC">
# ----------
# -- MISC --
# ----------


class Dependency(models.Model):
    course1 = models.ForeignKey('Course', related_name='first_course', on_delete=models.CASCADE)
    course2 = models.ForeignKey('Course', related_name='second_course', on_delete=models.CASCADE)
    successive = models.BooleanField(verbose_name='Successifs?', default=False)
    ND = models.BooleanField(verbose_name='Jours differents', default=False)

    def __str__(self):
        return f"{self.course1} avant {self.course2}"


class CourseStartTimeConstraint(models.Model):
    # foreignkey instead of onetoone to leave room for a day attribute
    course_type = models.ForeignKey('CourseType', null=True, default=None, on_delete=models.CASCADE)
    allowed_start_times = ArrayField(models.PositiveSmallIntegerField(), blank=True)



class Regen(models.Model):

    department =  models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()
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
            pre = f'C,{self.fday}/{self.fmonth}/{self.fyear}'
        if self.stabilize:
            pre = f'S,{self.sday}/{self.smonth}/{self.syear}'
        if not self.full and not self.stabilize:
            pre = 'N'
        return pre

    def strplus(self):
        ret = f"Semaine {self.week} ({self.year}) : "

        if self.full:
            ret += f'Génération complète le ' + \
                f'{self.fday}/{self.fmonth}/{self.fyear}'
        elif self.stabilize:
            ret += 'Génération stabilisée le ' + \
                f'{self.sday}/{self.smonth}/{self.syear}'
        else:
            ret += "Pas de (re-)génération prévue"

        return ret

# </editor-fold desc="MISC">
