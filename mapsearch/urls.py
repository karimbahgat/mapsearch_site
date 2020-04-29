from django.urls import path

from . import views

urlpatterns = [
    path('', views.search, name='home'),
    path('', views.search, name='search'),
]
