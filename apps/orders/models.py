from django.db import models
from django.conf import settings
import uuid

class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = 'PLACED', 'Order Placed (ऑर्डर दर्ज)'
        CONFIRMED = 'CONFIRMED', 'Aggregated at Village Hub (ग्राम केंद्र में एकत्रित)'
        PICKUP_SCHEDULED = 'PICKUP_SCHEDULED', 'Pickup Scheduled (पिकअप निर्धारित)'
        IN_TRANSIT = 'IN_TRANSIT', 'In Cold Transit (रास्ते में)'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery (वितरण के लिए निकला)'
        DELIVERED = 'DELIVERED', 'Delivered (वितरित)'
        CANCELLED = 'CANCELLED', 'Cancelled (रद्द)'

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    farmer_payout_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    delivery_address = models.TextField()
    contact_phone = models.CharField(max_length=15)
    
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PLACED
    )
    payment_method = models.CharField(max_length=30, default='UPI_MOCK')
    is_paid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AGC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_weight_kg(self):
        return sum([item.quantity_kg for item in self.items.all()])

    def __str__(self):
        return f"Order #{self.order_number} - {self.consumer.get_full_name() or self.consumer.username} (₹{self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity_kg = models.DecimalField(max_digits=7, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    farmer_price_per_kg = models.DecimalField(max_digits=7, decimal_places=2)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2)
    farmer_subtotal = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f"{self.quantity_kg}kg {self.product.name} (Order #{self.order.order_number})"


class QualityDispute(models.Model):
    class IssueType(models.TextChoices):
        SPOILED_TRANSIT = 'SPOILED_TRANSIT', 'Spoiled or Bruised in Transit (पारगमन में खराब)'
        WEIGHT_SHORTAGE = 'WEIGHT_SHORTAGE', 'Weight Discrepancy (वजन में कमी)'
        POOR_GRADE = 'POOR_GRADE', 'Grade Lower than Specified (गुणवत्ता में अंतर)'
        OTHER = 'OTHER', 'Other Concern (अन्य शिकायत)'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Under Hub Review (समीक्षाधीन)'
        RESOLVED_REFUNDED = 'RESOLVED_REFUNDED', 'Approved & Refund Credited (स्वीकृत व रिफंड जारी)'
        REJECTED = 'REJECTED', 'Claim Rejected (अस्वीकृत)'

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='disputes'
    )
    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='filed_disputes'
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes'
    )
    issue_type = models.CharField(
        max_length=30,
        choices=IssueType.choices,
        default=IssueType.SPOILED_TRANSIT
    )
    description = models.TextField(help_text="Explain the quality or transit issue encountered")
    refund_amount_requested = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    resolution_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def resolve(self, is_approved, notes=""):
        from django.utils import timezone
        if is_approved:
            self.status = self.Status.RESOLVED_REFUNDED
        else:
            self.status = self.Status.REJECTED
        self.resolution_notes = notes
        self.resolved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Dispute #{self.id} on Order #{self.order.order_number} ({self.get_status_display()})"

