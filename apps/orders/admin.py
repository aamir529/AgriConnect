from django.contrib import admin
from .models import Order, OrderItem, QualityDispute

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity_kg', 'price_per_kg', 'farmer_price_per_kg', 'subtotal', 'farmer_subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'consumer', 'total_amount', 'farmer_payout_amount', 'status', 'payment_method', 'is_paid', 'created_at')
    list_filter = ('status', 'payment_method', 'is_paid', 'created_at')
    search_fields = ('order_number', 'consumer__username', 'contact_phone', 'delivery_address')
    inlines = [OrderItemInline]

@admin.register(QualityDispute)
class QualityDisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'consumer', 'issue_type', 'refund_amount_requested', 'status', 'created_at', 'resolved_at')
    list_filter = ('status', 'issue_type', 'created_at')
    search_fields = ('order__order_number', 'consumer__username', 'description')

