from django.urls import path
from . import views

urlpatterns = [
    path('', views.mandi_prices_view, name='mandi_prices'),
    path('api/recommend-price/', views.api_price_recommendation, name='api_price_recommendation'),
    path('api/sync-live/', views.api_sync_live_mandi, name='api_sync_live_mandi'),
]