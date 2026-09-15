from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.logistics.models import DeliveryAssignment

class Command(BaseCommand):
    help = "Seed Phase 4: Logistics Fleet Assignments and Batch Pickup Manifests"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Phase 4 data..."))

        try:
            driver_user = CustomUser.objects.get(username='delivery_rajesh')
            consumer_user = CustomUser.objects.get(username='consumer_priya')
            onion_product = Product.objects.filter(name__icontains='Onion').first()
            chilli_product = Product.objects.filter(name__icontains='Chilli').first()

            # Ensure all existing orders have delivery assignments
            orders = Order.objects.all()
            for order in orders:
                assignment, created = DeliveryAssignment.objects.get_or_create(
                    order=order,
                    defaults={
                        'delivery_person': driver_user,
                        'pickup_hub_name': 'Angara Digital CSC Aggregation Hub',
                        'vehicle_type': 'Tata Ace Cold Chain Mini-Van',
                        'vehicle_number': 'JH-01-EF-4921',
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  + Assigned Order #{order.order_number} to driver Rajesh Verma"))

            # Create an additional batch order if fewer than 2 orders
            if Order.objects.count() < 2 and onion_product:
                batch_order = Order.objects.create(
                    consumer=consumer_user,
                    total_amount=Decimal('420.00'),
                    farmer_payout_amount=Decimal('336.00'),
                    delivery_fee=Decimal('0.00'),
                    delivery_address='Office Suite 301, Tech Park, Namkum, Ranchi, 834010',
                    contact_phone='9800000004',
                    status=Order.Status.IN_TRANSIT,
                    payment_method='UPI_MOCK',
                    is_paid=True
                )

                OrderItem.objects.create(
                    order=batch_order,
                    product=onion_product,
                    quantity_kg=Decimal('10.00'),
                    price_per_kg=onion_product.consumer_price_per_kg,
                    farmer_price_per_kg=onion_product.farmer_base_price_per_kg,
                    subtotal=onion_product.consumer_price_per_kg * Decimal('10.00'),
                    farmer_subtotal=onion_product.farmer_base_price_per_kg * Decimal('10.00')
                )

                if chilli_product:
                    OrderItem.objects.create(
                        order=batch_order,
                        product=chilli_product,
                        quantity_kg=Decimal('2.00'),
                        price_per_kg=chilli_product.consumer_price_per_kg,
                        farmer_price_per_kg=chilli_product.farmer_base_price_per_kg,
                        subtotal=chilli_product.consumer_price_per_kg * Decimal('2.00'),
                        farmer_subtotal=chilli_product.farmer_base_price_per_kg * Decimal('2.00')
                    )

                DeliveryAssignment.objects.create(
                    order=batch_order,
                    delivery_person=driver_user,
                    pickup_hub_name='Angara Digital CSC Aggregation Hub',
                    vehicle_type='Tata Ace Cold Chain Mini-Van',
                    vehicle_number='JH-01-EF-4921',
                    picked_up_at=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f"  + Created Second Batch Order #{batch_order.order_number} (IN_TRANSIT)"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ~ Notice in seeding Phase 4: {e}"))

        self.stdout.write(self.style.SUCCESS("\nPhase 4 Seeding Complete!"))
