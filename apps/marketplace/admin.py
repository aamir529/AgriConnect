from django.contrib import admin
from .models import GroupBuyingPool, CustomerReview

@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer_name', 'reviewer_role', 'reviewer_location', 'rating', 'is_approved', 'is_featured', 'submitted_at']
    list_filter = ['reviewer_role', 'rating', 'is_approved', 'is_featured']
    list_editable = ['is_approved', 'is_featured']
    search_fields = ['reviewer_name', 'review_text', 'reviewer_location']
    readonly_fields = ['submitted_at', 'user']
    ordering = ['-submitted_at']

    actions = ['approve_selected', 'feature_selected', 'unapprove_selected']

    @admin.action(description='Approve selected reviews')
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Feature selected reviews on homepage')
    def feature_selected(self, request, queryset):
        queryset.update(is_approved=True, is_featured=True)

    @admin.action(description='Unapprove selected reviews')
    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False, is_featured=False)

@admin.register(GroupBuyingPool)
class GroupBuyingPoolAdmin(admin.ModelAdmin):
    list_display = ['product', 'status']