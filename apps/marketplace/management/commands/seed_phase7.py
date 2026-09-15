from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import CustomUser
from apps.products.models import Product
from apps.marketplace.models import GroupBuyingPool, GroupBuyingParticipant

class Command(BaseCommand):
    help = "Seed Phase 7: Community Group Buying Pools and Neighborhood Clusters"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Phase 7: Community Group Buying Pools..."))

        try:
            consumer_priya = CustomUser.objects.filter(username='consumer_priya').first()
            if not consumer_priya:
                consumer_priya = CustomUser.objects.first()

            tomato = Product.objects.filter(name__icontains='tomato').first()
            onion = Product.objects.filter(name__icontains='onion').first()

            if tomato:
                pool1, created = GroupBuyingPool.objects.get_or_create(
                    title="Morabadi Green Acres 50kg Tomato Bulk Pool",
                    defaults={
                        'product': tomato,
                        'apartment_cluster': "Green Acres Society, Morabadi, Ranchi",
                        'target_kg': Decimal('50.00'),
                        'current_kg': Decimal('35.00'),
                        'bulk_price_per_kg': Decimal('24.00'),
                        'status': GroupBuyingPool.Status.OPEN,
                        'expires_at': timezone.now() + timedelta(days=2),
                    }
                )
                if created and consumer_priya:
                    GroupBuyingParticipant.objects.create(
                        pool=pool1,
                        consumer=consumer_priya,
                        pledged_kg=Decimal('10.00')
                    )
                self.stdout.write(self.style.SUCCESS("  + Seeded 50kg Tomato Bulk Pool for Morabadi Green Acres (70% Pledged)"))

            if onion:
                pool2, created = GroupBuyingPool.objects.get_or_create(
                    title="Namkum Tech Enclave 80kg Onion Wholesale Crate",
                    defaults={
                        'product': onion,
                        'apartment_cluster': "Tech Enclave Towers, Namkum, Ranchi",
                        'target_kg': Decimal('80.00'),
                        'current_kg': Decimal('60.00'),
                        'bulk_price_per_kg': Decimal('26.00'),
                        'status': GroupBuyingPool.Status.OPEN,
                        'expires_at': timezone.now() + timedelta(days=3),
                    }
                )
                if created and consumer_priya:
                    GroupBuyingParticipant.objects.create(
                        pool=pool2,
                        consumer=consumer_priya,
                        pledged_kg=Decimal('15.00')
                    )
                self.stdout.write(self.style.SUCCESS("  + Seeded 80kg Onion Wholesale Crate for Namkum Tech Enclave (75% Pledged)"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ~ Notice in seeding Phase 7: {e}"))

        self.stdout.write(self.style.SUCCESS("\nPhase 7 Seeding Complete!"))
