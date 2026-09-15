from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_perishable', 'shelf_life_days')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'grade', 'available_quantity_kg', 'farmer_base_price_per_kg', 'consumer_price_per_kg', 'is_organic', 'is_active')
    list_filter = ('grade', 'is_organic', 'is_active', 'category')
    search_fields = ('name', 'farmer__user__username', 'variety')
