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