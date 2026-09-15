from django.urls import path
from . import views

urlpatterns = [
    path('dispatch/', views.dispatch_dashboard_view, name='dispatch_dashboard'),
    path('update/<int:order_id>/', views.update_delivery_status_view, name='update_delivery_status'),
    path('manifest/', views.batch_manifest_view, name='batch_manifest'),
    path('iot-telemetry/', views.iot_telemetry_view, name='iot_telemetry'),
]
