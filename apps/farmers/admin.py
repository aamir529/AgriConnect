from django.contrib import admin
from .models import FarmerProfile, FarmerSMSLog

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'facilitator', 'land_area_acres', 'primary_crops', 'is_assisted_only', 'total_sales_realization')
    list_filter = ('is_assisted_only', 'facilitator__village_name')
    search_fields = ('user__username', 'user__first_name', 'user__phone', 'primary_crops')

@admin.register(FarmerSMSLog)
class FarmerSMSLogAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'alert_type', 'phone_number', 'is_delivered', 'sent_at')
    list_filter = ('alert_type', 'is_delivered', 'sent_at')
    search_fields = ('farmer__user__username', 'phone_number', 'message_text')
