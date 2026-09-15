from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard_view, name='analytics_dashboard'),
    path('demand-forecast/', views.demand_forecast_view, name='demand_forecast'),
    path('api/predict-demand/', views.api_predict_demand, name='api_predict_demand'),
    path('sih-presentation/', views.sih_presentation_view, name='sih_presentation'),
]
