from django.urls import path
from . import views

app_name = 'spaces'

urlpatterns = [
    path('', views.space_list, name='list'),
    path('space/<int:pk>/', views.space_detail, name='detail'),
    path('space/add/', views.space_add, name='add'),
    path('space/<int:pk>/edit/', views.space_edit, name='edit'),
    path('space/<int:pk>/delete/', views.space_delete, name='delete'),
    path('space/<int:pk>/add-image/', views.space_add_image, name='add_image'),
]
