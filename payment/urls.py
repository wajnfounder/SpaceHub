from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('checkout/<int:booking_pk>/', views.checkout,        name='checkout'),
    path('success/<int:booking_pk>/',  views.payment_success, name='success'),
]
