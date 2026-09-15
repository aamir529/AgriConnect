from django.db import models
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    icon = models.CharField(max_length=50, default="fa-carrot", help_text="FontAwesome icon class")
    is_perishable = models.BooleanField(default=True)
    shelf_life_days = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    class QualityGrade(models.TextChoices):
        GRADE_A = 'A', 'Grade A (Premium / Fresh Pick)'
        GRADE_B = 'B', 'Grade B (Standard Market Grade)'
        GRADE_C = 'C', 'Grade C (Bulk / Processing Grade)'

    farmer = models.ForeignKey(
        'farmers.FarmerProfile',
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    name = models.CharField(max_length=120, help_text="Crop name, e.g. Fresh Hybrid Tomatoes")
    variety = models.CharField(max_length=100, blank=True, null=True, help_text="Variety e.g. Abhinav, Kufri Jyoti")
    description = models.TextField(blank=True, default="Freshly harvested produce directly aggregated at village hub.")
    grade = models.CharField(max_length=2, choices=QualityGrade.choices, default=QualityGrade.GRADE_A)
    
    # Quantities & Pricing
    available_quantity_kg = models.DecimalField(max_digits=8, decimal_places=2, help_text="Total available stock in kg")
    minimum_order_kg = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    
    farmer_base_price_per_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Direct payout received by farmer per kg (in ₹)"
    )
    consumer_price_per_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Final price paid by consumer per kg (in ₹)"
    )
    traditional_market_price_per_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=40.00,
        help_text="Retail supermarket benchmark price per kg for comparison (in ₹)"
    )
    
    # Harvest & Metadata
    harvest_date = models.DateField(help_text="Date of harvest")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    emoji_icon = models.CharField(max_length=10, default="🍅", help_text="Fallback emoji for quick display")
    is_organic = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Automatically calculate consumer price if not explicitly overridden:
        Consumer Price = Base + 5% VDF + 10% Logistics + 10% Platform
        """
        if not self.consumer_price_per_kg or self.consumer_price_per_kg <= self.farmer_base_price_per_kg:
            base = Decimal(str(self.farmer_base_price_per_kg))
            vdf_cut = base * Decimal('0.05')
            logistics = base * Decimal('0.10')
            platform = base * Decimal('0.10')
            self.consumer_price_per_kg = (base + vdf_cut + logistics + platform).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def calculate_price_breakdown(self):
        """
        Returns full supply chain rupee allocations and consumer savings percentages.
        """
        base = float(self.farmer_base_price_per_kg)
        vdf_cut = round(base * 0.05, 2)
        logistics = round(base * 0.10, 2)
        platform_fee = round(base * 0.10, 2)
        consumer_price = float(self.consumer_price_per_kg)
        traditional = float(self.traditional_market_price_per_kg)

        savings_rupees = round(traditional - consumer_price, 2) if traditional > consumer_price else 0.0
        savings_percent = round((savings_rupees / traditional) * 100, 1) if traditional > 0 else 0.0
        farmer_percentage = round((base / consumer_price) * 100, 1) if consumer_price > 0 else 75.0

        return {
            'farmer_take_home': base,
            'facilitator_fee': vdf_cut,
            'logistics_fee': logistics,
            'platform_fee': platform_fee,
            'consumer_price': consumer_price,
            'traditional_retail_price': traditional,
            'consumer_savings_rupees': savings_rupees,
            'consumer_savings_percent': savings_percent,
            'farmer_share_percent': farmer_percentage,
        }

    def __str__(self):
        return f"{self.name} - ₹{self.consumer_price_per_kg}/kg ({self.farmer.user.village_or_city})"
