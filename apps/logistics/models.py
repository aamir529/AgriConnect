from django.db import models
from django.conf import settings
from django.utils import timezone

class DeliveryAssignment(models.Model):
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='delivery_assignment'
    )
    delivery_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deliveries'
    )
    pickup_hub_name = models.CharField(
        max_length=150,
        default='Angara Digital CSC Aggregation Hub'
    )
    vehicle_type = models.CharField(
        max_length=80,
        default='Tata Ace Cold Chain Mini-Van'
    )
    vehicle_number = models.CharField(
        max_length=30,
        default='JH-01-EF-4921'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    driver_notes = models.TextField(blank=True, default='')

    def mark_picked_up(self):
        self.picked_up_at = timezone.now()
        self.save()

    def mark_delivered(self):
        self.delivered_at = timezone.now()
        self.save()

    def __str__(self):
        driver_name = self.delivery_person.get_full_name() if self.delivery_person else 'Unassigned'
        return f"Delivery Assignment #{self.order.order_number} -> {driver_name} ({self.vehicle_number})"
