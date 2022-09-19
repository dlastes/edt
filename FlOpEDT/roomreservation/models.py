from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.timing import Day


class RoomReservation(models.Model):
    responsible = models.ForeignKey('people.User', on_delete=models.CASCADE, related_name='reservationResp')
    room = models.ForeignKey('base.Room', on_delete=models.CASCADE, related_name='reservationRoom')
    reservation_type = models.ForeignKey('RoomReservationType', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    email = models.BooleanField(default=False)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    periodicity = models.ForeignKey("ReservationPeriodicity", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.room}-{self.date}  {self.start_time}/{self.end_time}"


class RoomReservationType(models.Model):
    name = models.CharField(max_length=30)
    bg_color = ColorField(default='#95a5a6')

    def __str__(self):
        return self.name


class ReservationPeriodicity(models.Model):
    class PeriodicityType(models.TextChoices):
        # EachDay = 'ED', _('Each day')
        ByWeek = 'BW', _('By week')
        EachMonthSameDate = 'EM', _('Each month at the same date')
        ByMonth = 'BM', _('By Month')

    class ByMonthX(models.IntegerChoices):
        First = 1, _('First')
        Second = 2, _('Second')
        Third = 3, _('Third')
        Fourth = 4, _('Fourth')
        AnteLast = -2, _('Ante Last')
        Last = -1, _('Last')

    periodicity_type = models.CharField(
        max_length=2,
        choices=PeriodicityType.choices,
        default=PeriodicityType.ByWeek,
    )
    start = models.DateField(blank=True)
    end = models.DateField(blank=True)

    ### ByWeek Paramaters ###
    # Jours de la semaine qui doivent être inclus dans la réservation ByWeek
    bw_weekdays = ArrayField(models.CharField(max_length=2,
                                              choices=Day.CHOICES), help_text="m, tu, w, th, f", blank=True, null=True)
    # La réservation ByWeek sera reproduite toutes les n semaines (avec n = bw_weeks_interval)
    bw_weeks_interval = models.PositiveSmallIntegerField(blank=True, null=True)

    ### ByMonth Paramaters ###
    # La réservation ByMonth est tous les Xe Y du mois
    bm_x_choice = models.SmallIntegerField(choices=ByMonthX.choices, blank=True, null=True)
    bm_day_choice = models.CharField(max_length=2, choices=Day.CHOICES, blank=True, null=True)
