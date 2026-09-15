from django.db import models
from django.conf import settings

class FarmerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farmer_profile'
    )
    facilitator = models.ForeignKey(
        'facilitators.FacilitatorProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='farmers',
        help_text="The Village Digital Facilitator managing this farmer's digital operations"
    )
    land_area_acres = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.5,
        help_text="Cultivable land area in acres"
    )
    primary_crops = models.CharField(
        max_length=255,
        default="Tomato, Potato, Onion",
        help_text="Major seasonal crops produced"
    )
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=60, blank=True, null=True)
    is_assisted_only = models.BooleanField(
        default=True,
        help_text="True if farmer relies on VDF/IVR and does not operate smartphone app directly"
    )
    total_sales_realization = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Cumulative farmer earnings in Rupees"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def active_products(self):
        return self.products.filter(is_active=True)

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} ({self.user.village_or_city or 'Village'})"


class FarmerSMSLog(models.Model):
    """
    Simulated SMS communication record sent to the farmer's basic phone.
    Guarantees that non-smartphone farmers receive transparent, timely transaction updates.
    """
    class AlertType(models.TextChoices):
        LISTING_CREATED = 'LISTING_CREATED', 'Listing Published (फसल सूची जारी)'
        ORDER_RECEIVED = 'ORDER_RECEIVED', 'Order Placed (ऑर्डर प्राप्त)'
        PICKUP_DONE = 'PICKUP_DONE', 'Produce Picked Up (फसल उठाई गई)'
        PAYMENT_REMITTED = 'PAYMENT_REMITTED', 'Bank/UPI Payment Received (भुगतान प्राप्त)'
        MARKET_ALERT = 'MARKET_ALERT', 'Mandi Price Advisory (मंडी भाव सूचना)'

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name='sms_logs'
    )
    alert_type = models.CharField(max_length=30, choices=AlertType.choices, default=AlertType.LISTING_CREATED)
    phone_number = models.CharField(max_length=15)
    message_text = models.TextField()
    is_delivered = models.BooleanField(default=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"SMS to {self.phone_number}: [{self.get_alert_type_display()}]"
