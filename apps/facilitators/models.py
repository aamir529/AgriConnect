from django.db import models
from django.conf import settings

class FacilitatorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='facilitator_profile'
    )
    village_name = models.CharField(max_length=120, help_text="Primary village assigned to this VDF")
    center_name = models.CharField(max_length=150, help_text="Name of CSC Center or Village Hub")
    assigned_district = models.CharField(max_length=100, default="Ranchi")
    commission_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=5.00,
        help_text="Facilitation & quality grading fee percentage (default 5%)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_farmers_count(self):
        return self.farmers.count()

    @property
    def total_active_listings(self):
        from apps.products.models import Product
        return Product.objects.filter(farmer__facilitator=self, is_active=True).count()

    @property
    def total_produce_volume_kg(self):
        from apps.products.models import Product
        from django.db.models import Sum
        total = Product.objects.filter(farmer__facilitator=self).aggregate(Sum('available_quantity_kg'))['available_quantity_kg__sum']
        return total or 0

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.village_name} VDF Hub)"
