from django.urls import path

from . import views

urlpatterns = [
    path('', views.search, name='home'),
    path('', views.search, name='search'),
    path('map/add/', views.map_add, name='map_add'),
    path('map/update/<int:pk>/about', views.map_update_about, name='map_update_about'),
    path('map/update/<int:pk>/georef/', views.map_update_georef, name='map_update_georef'),
    path('map/view/<int:pk>/', views.map_view, name='map_view'),
    path('map/view/<int:pk>/<str:tab>', views.map_view, name='map_view'),
    path('map/download/<int:pk>/georef/', views.map_download_georef, name='map_download_georef'),
    path('map/download/<int:pk>/thumb/', views.map_download_thumb, name='map_download_thumb'),
    path('scrape/', views.scrape, name='scrape'),
    path('search/text/', views.search_text, name='search_text'),
    path('layer/add/', views.layer_add, name='layer_add'),
    path('layer/edit/<int:pk>/', views.layer_edit, name='layer_edit'),
    path('layer/download/<int:pk>/trans/', views.layer_download_trans, name='layer_download_trans'),
    path('layer/delete/<int:pk>/', views.layer_delete, name='layer_delete'),
]
