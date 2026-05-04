from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:space_pk>/', views.booking_create, name='create'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('owner/', views.owner_bookings, name='owner_bookings'),
    path('<int:pk>/confirm/', views.booking_confirm, name='confirm'),
    path('<int:pk>/cancel/', views.booking_cancel, name='cancel'),
    path('<int:pk>/complete/', views.booking_complete, name='complete'),
]
