from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal

from apps.accounts.models import CustomUser
from apps.products.models import Product
from apps.orders.models import Order, OrderItem
from apps.market_intelligence.models import MarketBenchmarkPrice

class Command(BaseCommand):
    help = "Seed Phase 3: APMC Mandi Benchmark Prices and Sample Consumer Orders"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Phase 3 data..."))

        # 1. Seed APMC Mandi Benchmark Prices
        mandi_benchmarks = [
            {
                'crop_name': 'Fresh Hybrid Tomatoes',
                'mandi_name': 'Ranchi Pandra APMC Mandi',
                'district': 'Ranchi',
                'modal_price_per_kg': Decimal('22.00'),
                'min_price_per_kg': Decimal('18.00'),
                'max_price_per_kg': Decimal('25.00'),
                'retail_estimated_price_per_kg': Decimal('42.00'),
            },
            {
                'crop_name': 'Kufri Jyoti Potatoes',
                'mandi_name': 'Ranchi Pandra APMC Mandi',
                'district': 'Ranchi',
                'modal_price_per_kg': Decimal('16.00'),
                'min_price_per_kg': Decimal('14.00'),
                'max_price_per_kg': Decimal('18.00'),
                'retail_estimated_price_per_kg': Decimal('30.00'),
            },
            {
                'crop_name': 'Nashik Red Onions',
                'mandi_name': 'Ranchi Pandra APMC Mandi',
                'district': 'Ranchi',
                'modal_price_per_kg': Decimal('26.00'),
                'min_price_per_kg': Decimal('22.00'),
                'max_price_per_kg': Decimal('30.00'),
                'retail_estimated_price_per_kg': Decimal('45.00'),
            },
            {
                'crop_name': 'Spicy Green Chillies',
                'mandi_name': 'Ranchi Pandra APMC Mandi',
                'district': 'Ranchi',
                'modal_price_per_kg': Decimal('55.00'),
                'min_price_per_kg': Decimal('45.00'),
                'max_price_per_kg': Decimal('65.00'),
                'retail_estimated_price_per_kg': Decimal('95.00'),
            },
            {
                'crop_name': 'Fresh Cauliflower',
                'mandi_name': 'Ramgarh District Mandi',
                'district': 'Ramgarh',
                'modal_price_per_kg': Decimal('24.00'),
                'min_price_per_kg': Decimal('20.00'),
                'max_price_per_kg': Decimal('28.00'),
                'retail_estimated_price_per_kg': Decimal('45.00'),
            },
            {
                'crop_name': 'Green Peas (Matar)',
                'mandi_name': 'Hazaribagh APMC Market',
                'district': 'Hazaribagh',
                'modal_price_per_kg': Decimal('48.00'),
                'min_price_per_kg': Decimal('40.00'),
                'max_price_per_kg': Decimal('55.00'),
                'retail_estimated_price_per_kg': Decimal('80.00'),
            },
        ]

        for m_data in mandi_benchmarks:
            obj, created = MarketBenchmarkPrice.objects.get_or_create(
                crop_name=m_data['crop_name'],
                mandi_name=m_data['mandi_name'],
                defaults=m_data
            )
            self.stdout.write(self.style.SUCCESS(f"  + Mandi Benchmark: {obj.crop_name} @ Rs {obj.modal_price_per_kg}/kg"))

        # 2. Seed Sample Order for consumer_priya
        try:
            priya_user = CustomUser.objects.get(username='consumer_priya')
            tomato_product = Product.objects.filter(name__icontains='Tomato').first()
            potato_product = Product.objects.filter(name__icontains='Potato').first()

            if tomato_product and potato_product:
                # Check if an order already exists
                existing_order = Order.objects.filter(consumer=priya_user).first()
                if not existing_order:
                    sample_order = Order.objects.create(
                        consumer=priya_user,
                        total_amount=Decimal('487.50'),
                        farmer_payout_amount=Decimal('390.00'),
                        delivery_fee=Decimal('0.00'),
                        delivery_address='Flat 402, Green Acres Apt, Morabadi, Ranchi, 834008',
                        contact_phone='9800000004',
                        status=Order.Status.CONFIRMED,
                        payment_method='UPI_MOCK',
                        is_paid=True
                    )

                    # 10 kg tomatoes
                    OrderItem.objects.create(
                        order=sample_order,
                        product=tomato_product,
                        quantity_kg=Decimal('10.00'),
                        price_per_kg=tomato_product.consumer_price_per_kg,
                        farmer_price_per_kg=tomato_product.farmer_base_price_per_kg,
                        subtotal=tomato_product.consumer_price_per_kg * Decimal('10.00'),
                        farmer_subtotal=tomato_product.farmer_base_price_per_kg * Decimal('10.00')
                    )

                    # 10 kg potatoes
                    OrderItem.objects.create(
                        order=sample_order,
                        product=potato_product,
                        quantity_kg=Decimal('10.00'),
                        price_per_kg=potato_product.consumer_price_per_kg,
                        farmer_price_per_kg=potato_product.farmer_base_price_per_kg,
                        subtotal=potato_product.consumer_price_per_kg * Decimal('10.00'),
                        farmer_subtotal=potato_product.farmer_base_price_per_kg * Decimal('10.00')
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Seeded Sample Order #{sample_order.order_number} for Priya Sharma"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ~ Order seeding notice: {e}"))

        self.stdout.write(self.style.SUCCESS("\nPhase 3 Seeding Complete!"))
