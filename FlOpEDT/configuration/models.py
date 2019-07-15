from django.db import models

# Create your models here.


class UpdateConfig(models.Model):
    # date = models.CharField(max_length=200)
    date = models.DateTimeField()
    is_planif_update = models.BooleanField()

