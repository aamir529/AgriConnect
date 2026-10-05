import os
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.farmers.models import FarmerProfile
from apps.products.models import Product, Category
from apps.marketplace.models import GroupBuyingPool, GroupBuyingParticipant


class Command(BaseCommand):
    help = "Seed and synchronize realistic Community Group Buying Pools (safe to run multiple times)"

    def handle(self, *args, **options):
        # 1. Categories
        cat_veg, _ = Category.objects.get_or_create(
            name='Fresh Vegetables',
            defaults={
                'icon': 'fa-carrot',
                'is_perishable': True,
                'shelf_life_days': 5,
                'description': 'Direct farm harvested seasonal vegetables',
            }
        )

        # 2. Farmers / Growers
        # Grower 1: Ramesh Kumar
        farmer_ramesh_user = CustomUser.objects.filter(username='farmer_ramesh').first()
        if not farmer_ramesh_user:
            farmer_ramesh_user = CustomUser.objects.filter(first_name='Ramesh', last_name='Kumar').first()
        if not farmer_ramesh_user:
            farmer_ramesh_user = CustomUser.objects.create_user(
                username='farmer_ramesh',
                password='farmer123',
                first_name='Ramesh',
                last_name='Kumar',
                phone='9800000003',
                role=CustomUser.Role.FARMER,
                village_or_city='Jonha',
                district='Ranchi',
                state='Jharkhand',
                pincode='835103',
                preferred_language='Hindi',
                is_verified=True,
            )
        farmer_ramesh_profile, _ = FarmerProfile.objects.get_or_create(
            user=farmer_ramesh_user,
            defaults={
                'primary_crops': 'Tomato, Cauliflower, Brinjal',
                'land_area_acres': Decimal('2.0'),
            }
        )

        # Grower 2: Birsa Munda
        farmer_birsa_user = CustomUser.objects.filter(username='farmer_birsa').first()
        if not farmer_birsa_user:
            farmer_birsa_user = CustomUser.objects.filter(first_name='Birsa', last_name='Munda').first()
        if not farmer_birsa_user:
            farmer_birsa_user = CustomUser.objects.create_user(
                username='farmer_birsa',
                password='farmer123',
                first_name='Birsa',
                last_name='Munda',
                phone='9800000013',
                role=CustomUser.Role.FARMER,
                village_or_city='Getalsud',
                district='Ranchi',
                state='Jharkhand',
                pincode='835103',
                preferred_language='Hindi',
                is_verified=True,
            )
        farmer_birsa_profile, _ = FarmerProfile.objects.get_or_create(
            user=farmer_birsa_user,
            defaults={
                'primary_crops': 'Potato, Red Onion, Ginger',
                'land_area_acres': Decimal('3.0'),
            }
        )

        # 3. Products
        # Product 1: Fresh Hybrid Tomatoes
        tomato_product = Product.objects.filter(name__iexact='Fresh Hybrid Tomatoes').first()
        if not tomato_product:
            tomato_product = Product.objects.filter(name__icontains='tomato').first()
        if not tomato_product:
            tomato_product = Product.objects.create(
                farmer=farmer_ramesh_profile,
                category=cat_veg,
                name='Fresh Hybrid Tomatoes',
                variety='Abhinav Hybrid F1',
                available_quantity_kg=Decimal('450.00'),
                minimum_order_kg=Decimal('5.00'),
                farmer_base_price_per_kg=Decimal('25.00'),
                consumer_price_per_kg=Decimal('31.25'),
                traditional_market_price_per_kg=Decimal('42.00'),
                harvest_date=timezone.now().date(),
                emoji_icon='🍅',
                is_organic=True,
                is_active=True,
            )
        else:
            if tomato_product.consumer_price_per_kg != Decimal('31.25'):
                tomato_product.consumer_price_per_kg = Decimal('31.25')
                tomato_product.save(update_fields=['consumer_price_per_kg'])
            if not tomato_product.farmer:
                tomato_product.farmer = farmer_ramesh_profile
                tomato_product.save(update_fields=['farmer'])

        # Product 2: Nashik Red Onions
        onion_product = Product.objects.filter(name__iexact='Nashik Red Onions').first()
        if not onion_product:
            onion_product = Product.objects.filter(name__icontains='onion').first()
        if not onion_product:
            onion_product = Product.objects.create(
                farmer=farmer_birsa_profile,
                category=cat_veg,
                name='Nashik Red Onions',
                variety='Garwa High-Storage Red',
                available_quantity_kg=Decimal('800.00'),
                minimum_order_kg=Decimal('5.00'),
                farmer_base_price_per_kg=Decimal('28.00'),
                consumer_price_per_kg=Decimal('35.00'),
                traditional_market_price_per_kg=Decimal('48.00'),
                harvest_date=timezone.now().date(),
                emoji_icon='🧅',
                is_organic=False,
                is_active=True,
            )
        else:
            if onion_product.consumer_price_per_kg != Decimal('35.00'):
                onion_product.consumer_price_per_kg = Decimal('35.00')
                onion_product.save(update_fields=['consumer_price_per_kg'])
            if not onion_product.farmer:
                onion_product.farmer = farmer_birsa_profile
                onion_product.save(update_fields=['farmer'])

        # 4. Consumer user for pledges
        consumer_user = CustomUser.objects.filter(username='consumer_priya').first()
        if not consumer_user:
            consumer_user = CustomUser.objects.filter(role=CustomUser.Role.CONSUMER).first()
        if not consumer_user:
            consumer_user = CustomUser.objects.create_user(
                username='consumer_priya',
                password='consumer123',
                first_name='Priya',
                last_name='Sharma',
                phone='9800000004',
                role=CustomUser.Role.CONSUMER,
                village_or_city='Morabadi, Ranchi',
                district='Ranchi',
                state='Jharkhand',
                pincode='834008',
                preferred_language='English',
                is_verified=True,
            )

        # 5. Group Buying Pools
        # Pool 1: Morabadi Green Acres 50kg Tomato Bulk Pool
        pool1, _ = GroupBuyingPool.objects.update_or_create(
            title="Morabadi Green Acres 50kg Tomato Bulk Pool",
            defaults={
                'product': tomato_product,
                'apartment_cluster': "Green Acres Society, Morabadi, Ranchi",
                'target_kg': Decimal('50.00'),
                'current_kg': Decimal('35.00'),
                'bulk_price_per_kg': Decimal('24.00'),
                'status': GroupBuyingPool.Status.OPEN,
                'dispatch_time': 'Today 6 PM',
                'expires_at': timezone.now() + timedelta(days=2),
            }
        )

        # Pool 2: Namkum Tech Enclave 80kg Onion Wholesale Crate
        pool2, _ = GroupBuyingPool.objects.update_or_create(
            title="Namkum Tech Enclave 80kg Onion Wholesale Crate",
            defaults={
                'product': onion_product,
                'apartment_cluster': "Tech Enclave Towers, Namkum, Ranchi",
                'target_kg': Decimal('80.00'),
                'current_kg': Decimal('70.00'),
                'bulk_price_per_kg': Decimal('26.00'),
                'status': GroupBuyingPool.Status.OPEN,
                'dispatch_time': 'Today 6 PM',
                'expires_at': timezone.now() + timedelta(days=3),
            }
        )

        # 6. Participants / Pledges
        if consumer_user:
            GroupBuyingParticipant.objects.update_or_create(
                pool=pool1,
                consumer=consumer_user,
                defaults={
                    'pledged_kg': Decimal('35.00'),
                    'status': GroupBuyingParticipant.Status.PLEDGED,
                }
            )
            GroupBuyingParticipant.objects.update_or_create(
                pool=pool2,
                consumer=consumer_user,
                defaults={
                    'pledged_kg': Decimal('70.00'),
                    'status': GroupBuyingParticipant.Status.PLEDGED,
                }
            )

        def print_check(item):
            try:
                self.stdout.write(self.style.SUCCESS(f"✓ {item}"))
            except UnicodeEncodeError:
                self.stdout.write(self.style.SUCCESS(f"+ {item}"))

        # 7. Print requested formatted summary output
        self.stdout.write("========================================")
        self.stdout.write("AgriConnect Group Buying Seed")
        self.stdout.write("========================================")
        print_check(tomato_product.name)
        print_check(onion_product.name)
        print_check(farmer_ramesh_user.get_full_name() or farmer_ramesh_user.username)
        print_check(farmer_birsa_user.get_full_name() or farmer_birsa_user.username)
        print_check("Green Acres Society")
        print_check("Tech Enclave Towers")
        print_check("Tomato Group Pool")
        print_check("Onion Group Pool\n")
        self.stdout.write(self.style.SUCCESS("2 group buying pools created/updated."))
        self.stdout.write("========================================")
