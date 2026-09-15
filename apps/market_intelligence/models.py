from django.db import models
from django.utils import timezone

class MarketBenchmarkPrice(models.Model):
    crop_name = models.CharField(max_length=100, help_text="e.g. Tomato, Potato, Onion")
    mandi_name = models.CharField(max_length=120, help_text="e.g. Ranchi Pandra APMC Mandi")
    district = models.CharField(max_length=100, default="Ranchi")
    state = models.CharField(max_length=100, default="Jharkhand")
    modal_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2, help_text="Most common wholesale mandi rate")
    min_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    max_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    retail_estimated_price_per_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Typical consumer supermarket / retail price in nearby urban areas"
    )
    recorded_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-recorded_date', 'crop_name']

    def __str__(self):
        return f"{self.crop_name} @ {self.mandi_name} (₹{self.modal_price_per_kg}/kg on {self.recorded_date})"
