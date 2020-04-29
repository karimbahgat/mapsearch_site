from django.db import models

# Create your models here.

class Map(models.Model):
    url = models.URLField(blank=True)
    thumbnail = models.BinaryField(blank=True)

