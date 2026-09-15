from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.facilitator_dashboard_view, name='facilitator_dashboard'),
    path('register-farmer/', views.register_farmer_view, name='facilitator_register_farmer'),
    path('onboard-farmer/', views.register_farmer_view, name='facilitator_onboard_farmer'),
    path('add-listing/', views.add_listing_view, name='facilitator_add_listing'),
    path('assisted-listing/', views.add_listing_view, name='facilitator_assisted_listing'),
    path('ivr-simulator/', views.ivr_simulator_view, name='ivr_simulator'),
    path('api/ivr-action/', views.ivr_api_action, name='ivr_api_action'),
]
