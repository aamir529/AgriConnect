from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        FARMER = 'FARMER', 'Farmer (किसान)'
        FACILITATOR = 'FACILITATOR', 'Village Digital Facilitator (VDF / ग्राम मित्र)'
        CONSUMER = 'CONSUMER', 'Consumer / Buyer (ग्राहक)'
        DELIVERY = 'DELIVERY', 'Delivery Partner (वितरण साथी)'
        ADMIN = 'ADMIN', 'Platform Administrator (प्रशासक)'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONSUMER,
        help_text="User's primary operational role on AgriConnect"
    )
    phone = models.CharField(
        max_length=15,
        unique=True,
        help_text="Primary phone number (used for SMS alerts and IVR mapping)"
    )
    village_or_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Village / City")
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True, default="Jharkhand")
    pincode = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True, verbose_name="Detailed Address / Landmark")
    preferred_language = models.CharField(
        max_length=30,
        choices=[
            ('Hindi', 'हिंदी (Hindi)'),
            ('English', 'English'),
            ('Bengali', 'বাংলা (Bengali)'),
            ('Santhali', 'ᱥᱟᱱᱛᱟᱲᱤ (Santhali)'),
        ],
        default='Hindi'
    )
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False, help_text="Verified by Village Facilitator or Admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_farmer(self):
        return self.role == self.Role.FARMER

    @property
    def is_facilitator(self):
        return self.role == self.Role.FACILITATOR

    @property
    def is_consumer(self):
        return self.role == self.Role.CONSUMER

    @property
    def is_delivery(self):
        return self.role == self.Role.DELIVERY

    @property
    def is_platform_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def get_role_badge_class(self):
        mapping = {
            self.Role.FARMER: 'badge-farmer',
            self.Role.FACILITATOR: 'badge-facilitator',
            self.Role.CONSUMER: 'badge-consumer',
            self.Role.DELIVERY: 'badge-delivery',
            self.Role.ADMIN: 'badge-admin',
        }
        return mapping.get(self.role, 'badge-consumer')

    def __str__(self):
        full_name = self.get_full_name() or self.username
        location = f" ({self.village_or_city})" if self.village_or_city else ""
        return f"{full_name}{location} - [{self.get_role_display()}]"
