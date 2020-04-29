from django.db import models

# Create your models here.

class Map(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True)
    thumbnail = models.BinaryField(null=True, blank=True)

    georeferenced = models.DateTimeField(null=True)
    layout = models.TextField(blank=True, null=True)
    gcps = models.TextField(blank=True, null=True)
    transform = models.TextField(blank=True, null=True)
    footprint = models.TextField(blank=True, null=True)


