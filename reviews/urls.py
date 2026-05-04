from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:space_pk>/', views.review_add, name='add'),
    path('<int:pk>/delete/', views.review_delete, name='delete'),
]
