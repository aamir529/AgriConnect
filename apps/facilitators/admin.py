from django.contrib import admin
from .models import FacilitatorProfile

@admin.register(FacilitatorProfile)
class FacilitatorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'village_name', 'center_name', 'assigned_district', 'commission_percentage', 'is_active')
    list_filter = ('is_active', 'assigned_district')
    search_fields = ('user__username', 'user__first_name', 'village_name', 'center_name')
