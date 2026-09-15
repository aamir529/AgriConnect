from django.contrib import admin
from .models import DeliveryAssignment

@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_person', 'pickup_hub_name', 'vehicle_number', 'vehicle_type', 'assigned_at', 'picked_up_at', 'delivered_at')
    list_filter = ('vehicle_type', 'assigned_at', 'picked_up_at', 'delivered_at')
    search_fields = ('order__order_number', 'delivery_person__username', 'vehicle_number', 'pickup_hub_name')
