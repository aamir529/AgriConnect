from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.farmer_dashboard_view, name='farmer_dashboard'),
    path('passbook/', views.farmer_passbook_view, name='farmer_passbook'),
    path('crop-doctor/', views.crop_doctor_view, name='crop_doctor'),
]
