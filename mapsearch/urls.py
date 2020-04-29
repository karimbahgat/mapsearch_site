from django.urls import path

from . import views

urlpatterns = [
    path('', views.search, name='home'),
    path('', views.search, name='search'),
    path('map/view/<int:pk>/', views.map_view, name='map_view'),
]
