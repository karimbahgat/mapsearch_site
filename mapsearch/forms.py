from django import forms
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
        widgets = {
            'legend_symbol': forms.Textarea(attrs={'rows':3, 'cols':20}),
            'name': forms.Textarea(attrs={'rows':3, 'cols':20}),
            'comment': forms.Textarea(attrs={'rows':3, 'cols':20}),
        }
