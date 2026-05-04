from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('toggle/<int:space_pk>/', views.toggle_favorite, name='toggle'),
    path('',                        views.my_favorites,    name='list'),
]
