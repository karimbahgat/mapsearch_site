from django.db import models

# Create your models here.

class Map(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    xmin = models.FloatField(null=True)
    ymin = models.FloatField(null=True)
    xmax = models.FloatField(null=True)
    ymax = models.FloatField(null=True)
    thumbnail = models.BinaryField(null=True, blank=True)

    georeferenced = models.DateTimeField(null=True)
    layout = models.TextField(blank=True, null=True)
    gcps = models.TextField(blank=True, null=True)
    transform = models.TextField(blank=True, null=True)
    footprint = models.TextField(blank=True, null=True)

class Text(models.Model):
    map = models.ForeignKey('Map', on_delete=models.CASCADE, related_name='texts')
    text = models.TextField(null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=25)
    fontheight = models.IntegerField(null=True)
    geom = models.TextField(blank=True, null=True)

class Layer(models.Model):
    map = models.ForeignKey('Map', on_delete=models.CASCADE, related_name='layers')
    name = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=30, choices=[('Point','Point'),
                                                    ('LineString','LineString'),
                                                    ('Polygon','Polygon')])
    legend_description = models.ManyToManyField(Text, blank=True)
    legend_symbol = models.TextField(blank=True, null=True) # geojson coords to image legend symbol
    comment = models.TextField(null=True, blank=True)

    def to_geojson(self):
        import json
        return {'type':'FeatureCollection',
                'features':[feat.to_geojson() for feat in self.features.all()]}

class Feature(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    layer = models.ForeignKey('Layer', on_delete=models.CASCADE, related_name='features')
    geom = models.TextField(blank=True, null=True)
    label = models.ManyToManyField(Text, blank=True)

    def to_geojson(self):
        import json
        return {'type':'Feature',
                'properties':{'id':self.pk},
                'geometry':json.loads(self.geom)
                }

    
