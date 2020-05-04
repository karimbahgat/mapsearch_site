from django.forms import ModelForm

from .models import Map, Layer, Feature

class MapForm(ModelForm):
    class Meta:
        model = Map
        exclude = []

class LayerForm(ModelForm):
    class Meta:
        model = Layer
        exclude = []
