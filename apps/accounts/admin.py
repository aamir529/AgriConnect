from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'phone', 'role', 'village_or_city', 'district', 'preferred_language', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'state', 'preferred_language', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'village_or_city', 'district')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('AgriConnect Operational Info', {
            'fields': (
                'role',
                'phone',
                'village_or_city',
                'district',
                'state',
                'pincode',
                'address',
                'preferred_language',
                'profile_photo',
                'is_verified',
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('AgriConnect Operational Info', {
            'fields': (
                'role',
                'phone',
                'village_or_city',
                'district',
                'state',
                'pincode',
                'preferred_language',
            ),
        }),
    )
