from django.contrib import admin
from .models import GroupBuyingPool, GroupBuyingParticipant, CustomerReview

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
    list_display = [
        'title',
        'product',
        'get_grower',
        'apartment_cluster',
        'target_kg',
        'current_kg',
        'bulk_price_per_kg',
        'get_retail_price',
        'dispatch_time',
        'status',
        'get_progress',
    ]
    list_filter = ['status', 'product__category', 'dispatch_time', 'created_at']
    search_fields = [
        'title',
        'apartment_cluster',
        'product__name',
        'product__farmer__user__first_name',
        'product__farmer__user__last_name',
    ]
    list_editable = ['status', 'current_kg', 'bulk_price_per_kg', 'dispatch_time']
    readonly_fields = ['created_at', 'updated_at', 'progress_percent', 'remaining_kg']
    fieldsets = (
        ('Pool Details', {
            'fields': ('title', 'product', 'apartment_cluster', 'status')
        }),
        ('Quantity & Pricing', {
            'fields': ('target_kg', 'current_kg', 'bulk_price_per_kg', 'progress_percent', 'remaining_kg')
        }),
        ('Schedule & Logistics', {
            'fields': ('dispatch_time', 'expires_at', 'created_at', 'updated_at')
        }),
    )

    @admin.display(description='Grower / Farmer')
    def get_grower(self, obj):
        return obj.grower_name

    @admin.display(description='Retail Price')
    def get_retail_price(self, obj):
        return f"₹{obj.single_retail_price}/kg"

    @admin.display(description='Progress')
    def get_progress(self, obj):
        return f"{obj.progress_percent}%"


@admin.register(GroupBuyingParticipant)
class GroupBuyingParticipantAdmin(admin.ModelAdmin):
    list_display = ['pool', 'consumer', 'pledged_kg', 'status', 'joined_at']
    list_filter = ['status', 'joined_at', 'pool']
    search_fields = ['consumer__username', 'consumer__first_name', 'consumer__last_name', 'pool__title']
    list_editable = ['status', 'pledged_kg']
    readonly_fields = ['joined_at']