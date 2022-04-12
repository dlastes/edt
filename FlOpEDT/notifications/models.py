from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from base.timing import Day


# <editor-fold desc="BACKUP">
# ------------
# -- BACKUP --
# ------------

class BackUpModif(models.Model):
    week = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),
                                                        MaxValueValidator(53)],
                                            verbose_name=_('Week number'))
    year = models.PositiveSmallIntegerField()
    day = models.CharField(max_length=2,
                           choices=Day.CHOICES,
                           default=Day.MONDAY)
    module_abbrev = models.CharField(max_length=100,
                                     verbose_name=_('Abbreviation'))
    tutor_username = models.CharField(max_length=150,
                                      null=True)
    supp_tutor_usernames = ArrayField(models.CharField(max_length=10), null=True)
    start_time = models.PositiveSmallIntegerField()
    room_name = models.CharField(max_length=50,
                                 null=True)
    group_name = models.CharField(max_length=100)
    department_abbrev = models.CharField(max_length=7)
    train_prog_name = models.CharField(max_length=50)
    new = models.BooleanField(default=True)

    def __str__(self):
        return ("Module : " + str(self.module_abbrev) +
                " | Room : " + str(self.room_name) +
                " | Tutor : " + str(self.tutor_username))

    def __eq__(self, other):
        return self.week == other.week and self.year == other.year and self.day == other.day \
               and self.module_abbrev == other.module_abbrev and self.tutor_username == other.tutor_username \
               and self.supp_tutor_usernames == other.supp_tutor_usernames and self.start_time == other.start_time \
               and self.group_name == other.group_name \
               and self.department_abbrev == other.department_abbrev and self.train_prog_name == other.train_prog_name
        # and self.room_name == other.room_name \

    def __hash__(self):
        return hash(f"{self.week} {self.year} {self.day} {self.module_abbrev} {self.tutor_username} "
                    f"{self.supp_tutor_usernames} {self.start_time} {self.group_name} "
                    f"{self.department_abbrev} {self.train_prog_name}")


# </editor-fold desc="BACKUP">