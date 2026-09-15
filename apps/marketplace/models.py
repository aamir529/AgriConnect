from django.db import models
from django.conf import settings
from django.utils import timezone

class GroupBuyingPool(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Pledging Open (भागीदारी जारी)'
        LOCKED_FULL = 'LOCKED_FULL', 'Target Reached & Locked (लक्ष्य पूर्ण)'
        DISPATCHED = 'DISPATCHED', 'Batch In Transit (डिस्पैच हुआ)'

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='group_buying_pools'
    )
    title = models.CharField(max_length=150, help_text="e.g. Morabadi Sunday 50kg Tomato Bulk Pool")
    apartment_cluster = models.CharField(max_length=180, help_text="e.g. Green Acres Society, Morabadi, Ranchi")
    target_kg = models.DecimalField(max_digits=7, decimal_places=2, default=50.00)
    current_kg = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    bulk_price_per_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Discounted community bulk price (15% lower than single retail)"
    )
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @property
    def progress_percent(self):
        if self.target_kg > 0:
            pct = (float(self.current_kg) / float(self.target_kg)) * 100.0
            return min(100.0, round(pct, 1))
        return 0.0

    @property
    def remaining_kg(self):
        return max(0.0, round(float(self.target_kg) - float(self.current_kg), 1))

    def __str__(self):
        return f"{self.title} ({self.current_kg}/{self.target_kg} kg) - {self.get_status_display()}"


class GroupBuyingParticipant(models.Model):
    pool = models.ForeignKey(
        GroupBuyingPool,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_pledges'
    )
    pledged_kg = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consumer.get_full_name() or self.consumer.username} - {self.pledged_kg}kg ({self.pool.title})"

from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomerReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    ROLE_CHOICES = [
        ('CONSUMER', 'Consumer / Khareedaar'),
        ('FARMER', 'Kisan / Farmer'),
        ('FACILITATOR', 'Village Facilitator (VDF)'),
        ('SOCIETY', 'Housing Society Secretary'),
        ('OTHER', 'Other'),
    ]

    # Who is reviewing
    reviewer_name = models.CharField(max_length=120, help_text="Your name as you want it displayed")
    reviewer_role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='CONSUMER')
    reviewer_location = models.CharField(max_length=150, help_text="Village/City, District, State")
    # If logged in, link to user (optional)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviews'
    )

    # Review content
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    review_text = models.TextField(max_length=600, help_text="Share your experience (max 600 characters)")

    # Metadata
    submitted_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False, help_text="Only approved reviews appear on homepage")
    is_featured = models.BooleanField(default=False, help_text="Show in hero testimonials section")

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.reviewer_name} ({self.get_reviewer_role_display()}) - {self.rating} stars"

