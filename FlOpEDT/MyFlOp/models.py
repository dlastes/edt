from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.


class ModuleTutorRepartition(models.Model):
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    course_type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor', on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True,
        blank=True)
    year = models.PositiveSmallIntegerField(null=True,
                                            blank=True)
    courses_nb = models.PositiveSmallIntegerField()