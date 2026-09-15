from django.contrib import admin
from .models import MarketBenchmarkPrice

@admin.register(MarketBenchmarkPrice)
class MarketBenchmarkPriceAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'mandi_name', 'district', 'modal_price_per_kg', 'retail_estimated_price_per_kg', 'recorded_date')
    list_filter = ('district', 'recorded_date')
    search_fields = ('crop_name', 'mandi_name')
