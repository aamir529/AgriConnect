from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.products.models import Product
from apps.orders.models import Order, OrderItem, QualityDispute
from apps.logistics.models import DeliveryAssignment

class Command(BaseCommand):
    help = "Seed Phase 5: Historical Analytics Data and Quality Dispute Tickets"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Phase 5 Analytics & Dispute data..."))

        try:
            priya_user = CustomUser.objects.get(username='consumer_priya')
            driver_user = CustomUser.objects.get(username='delivery_rajesh')
            vdf_user = CustomUser.objects.get(username='vdf_sunil')

            tomato_prod = Product.objects.filter(name__icontains='Tomato').first()
            potato_prod = Product.objects.filter(name__icontains='Potato').first()
            onion_prod = Product.objects.filter(name__icontains='Onion').first()
            chilli_prod = Product.objects.filter(name__icontains='Chilli').first()

            # Create 2 additional completed historical orders for rich analytics
            if Order.objects.count() < 4 and tomato_prod and potato_prod:
                # Historical Order A (Delivered)
                order_a = Order.objects.create(
                    consumer=priya_user,
                    total_amount=Decimal('845.00'),
                    farmer_payout_amount=Decimal('633.75'),
                    delivery_fee=Decimal('0.00'),
                    delivery_address='Flat 402, Green Acres Apt, Morabadi, Ranchi',
                    contact_phone='9800000004',
                    status=Order.Status.DELIVERED,
                    payment_method='UPI_MOCK',
                    is_paid=True
                )

                OrderItem.objects.create(
                    order=order_a,
                    product=tomato_prod,
                    quantity_kg=Decimal('15.00'),
                    price_per_kg=tomato_prod.consumer_price_per_kg,
                    farmer_price_per_kg=tomato_prod.farmer_base_price_per_kg,
                    subtotal=tomato_prod.consumer_price_per_kg * Decimal('15.00'),
                    farmer_subtotal=tomato_prod.farmer_base_price_per_kg * Decimal('15.00')
                )

                OrderItem.objects.create(
                    order=order_a,
                    product=potato_prod,
                    quantity_kg=Decimal('20.00'),
                    price_per_kg=potato_prod.consumer_price_per_kg,
                    farmer_price_per_kg=potato_prod.farmer_base_price_per_kg,
                    subtotal=potato_prod.consumer_price_per_kg * Decimal('20.00'),
                    farmer_subtotal=potato_prod.farmer_base_price_per_kg * Decimal('20.00')
                )

                DeliveryAssignment.objects.create(
                    order=order_a,
                    delivery_person=driver_user,
                    pickup_hub_name='Angara Digital CSC Aggregation Hub',
                    vehicle_type='Tata Ace Cold Chain Mini-Van',
                    vehicle_number='JH-01-EF-4921',
                    picked_up_at=timezone.now(),
                    delivered_at=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f"  + Seeded Delivered Order #{order_a.order_number} (35 kg produce)"))

                # Historical Order B (Delivered)
                if onion_prod and chilli_prod:
                    order_b = Order.objects.create(
                        consumer=priya_user,
                        total_amount=Decimal('625.00'),
                        farmer_payout_amount=Decimal('468.75'),
                        delivery_fee=Decimal('0.00'),
                        delivery_address='Hinoo Main Road, Near Airport, Ranchi, 834002',
                        contact_phone='9800000004',
                        status=Order.Status.DELIVERED,
                        payment_method='UPI_MOCK',
                        is_paid=True
                    )

                    OrderItem.objects.create(
                        order=order_b,
                        product=onion_prod,
                        quantity_kg=Decimal('12.00'),
                        price_per_kg=onion_prod.consumer_price_per_kg,
                        farmer_price_per_kg=onion_prod.farmer_base_price_per_kg,
                        subtotal=onion_prod.consumer_price_per_kg * Decimal('12.00'),
                        farmer_subtotal=onion_prod.farmer_base_price_per_kg * Decimal('12.00')
                    )

                    OrderItem.objects.create(
                        order=order_b,
                        product=chilli_prod,
                        quantity_kg=Decimal('2.50'),
                        price_per_kg=chilli_prod.consumer_price_per_kg,
                        farmer_price_per_kg=chilli_prod.farmer_base_price_per_kg,
                        subtotal=chilli_prod.consumer_price_per_kg * Decimal('2.50'),
                        farmer_subtotal=chilli_prod.farmer_base_price_per_kg * Decimal('2.50')
                    )

                    DeliveryAssignment.objects.create(
                        order=order_b,
                        delivery_person=driver_user,
                        pickup_hub_name='Angara Digital CSC Aggregation Hub',
                        vehicle_type='Tata Ace Cold Chain Mini-Van',
                        vehicle_number='JH-01-EF-4921',
                        picked_up_at=timezone.now(),
                        delivered_at=timezone.now()
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Seeded Delivered Order #{order_b.order_number} (14.5 kg produce)"))

            # Seed Sample Quality Dispute Ticket
            first_order = Order.objects.first()
            if first_order and not QualityDispute.objects.exists():
                sample_item = first_order.items.first()
                sample_dispute = QualityDispute.objects.create(
                    order=first_order,
                    consumer=priya_user,
                    order_item=sample_item,
                    issue_type=QualityDispute.IssueType.SPOILED_TRANSIT,
                    description="2 kg of hybrid tomatoes sustained minor bruising during road transport over rural unpaved section.",
                    refund_amount_requested=Decimal('62.50'),
                    status=QualityDispute.Status.PENDING
                )
                self.stdout.write(self.style.SUCCESS(f"  + Seeded Quality Claim #{sample_dispute.id} (Under Hub Review)"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ~ Notice in seeding Phase 5: {e}"))

        self.stdout.write(self.style.SUCCESS("\nPhase 5 Seeding Complete!"))
