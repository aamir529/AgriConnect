from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal

from apps.accounts.models import CustomUser
from apps.facilitators.models import FacilitatorProfile
from apps.farmers.models import FarmerProfile, FarmerSMSLog
from apps.products.models import Category, Product

class Command(BaseCommand):
    help = "Seed Phase 2 data: Facilitator profile, Farmer profiles, Categories, Produce batches, and SMS logs"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Phase 2 data..."))

        # 1. Facilitator Profile for vdf_sunil
        try:
            sunil_user = CustomUser.objects.get(username='vdf_sunil')
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR("vdf_sunil not found! Run 'python manage.py seed_phase1' first."))
            return

        vdf_profile, _ = FacilitatorProfile.objects.get_or_create(
            user=sunil_user,
            defaults={
                'village_name': 'Angara',
                'center_name': 'Angara Digital CSC Hub',
                'assigned_district': 'Ranchi',
                'commission_percentage': Decimal('5.00'),
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  + Configured Facilitator Hub: {vdf_profile.center_name}"))

        # 2. Farmer Profiles
        # 2a. Ramesh Kumar
        ramesh_user = CustomUser.objects.get(username='farmer_ramesh')
        ramesh_profile, _ = FarmerProfile.objects.get_or_create(
            user=ramesh_user,
            defaults={
                'facilitator': vdf_profile,
                'land_area_acres': Decimal('2.5'),
                'primary_crops': 'Tomato, Potato, Cauliflower',
                'bank_account_number': '34901234021',
                'bank_ifsc': 'SBIN0001234',
                'upi_id': '9800000003@upi',
                'is_assisted_only': True,
                'total_sales_realization': Decimal('14500.00'),
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  + Configured Farmer: Ramesh Kumar"))

        # 2b. Sita Devi
        sita_user, _ = CustomUser.objects.get_or_create(
            username='farmer_sita',
            defaults={
                'first_name': 'Sita',
                'last_name': 'Devi',
                'phone': '9800000012',
                'role': CustomUser.Role.FARMER,
                'village_or_city': 'Jonha Village',
                'district': 'Ranchi',
                'preferred_language': 'Hindi',
                'is_verified': True,
            }
        )
        sita_user.set_password('farmer123')
        sita_user.save()

        sita_profile, _ = FarmerProfile.objects.get_or_create(
            user=sita_user,
            defaults={
                'facilitator': vdf_profile,
                'land_area_acres': Decimal('1.5'),
                'primary_crops': 'Tomato, Green Chilli, Okra',
                'upi_id': '9800000012@upi',
                'is_assisted_only': True,
                'total_sales_realization': Decimal('8400.00'),
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  + Configured Farmer: Sita Devi"))

        # 2c. Birsa Munda
        birsa_user, _ = CustomUser.objects.get_or_create(
            username='farmer_birsa',
            defaults={
                'first_name': 'Birsa',
                'last_name': 'Munda',
                'phone': '9800000013',
                'role': CustomUser.Role.FARMER,
                'village_or_city': 'Getalsud Village',
                'district': 'Ranchi',
                'preferred_language': 'Hindi',
                'is_verified': True,
            }
        )
        birsa_user.set_password('farmer123')
        birsa_user.save()

        birsa_profile, _ = FarmerProfile.objects.get_or_create(
            user=birsa_user,
            defaults={
                'facilitator': vdf_profile,
                'land_area_acres': Decimal('3.0'),
                'primary_crops': 'Potato, Red Onion, Ginger',
                'bank_account_number': '54120987112',
                'is_assisted_only': True,
                'total_sales_realization': Decimal('19200.00'),
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  + Configured Farmer: Birsa Munda"))

        # 3. Categories
        cat_veg, _ = Category.objects.get_or_create(
            name='Fresh Vegetables',
            defaults={'icon': 'fa-carrot', 'is_perishable': True, 'shelf_life_days': 5}
        )
        cat_fruit, _ = Category.objects.get_or_create(
            name='Orchard Fruits',
            defaults={'icon': 'fa-apple-whole', 'is_perishable': True, 'shelf_life_days': 8}
        )
        cat_grains, _ = Category.objects.get_or_create(
            name='Grains & Pulses',
            defaults={'icon': 'fa-wheat-awn', 'is_perishable': False, 'shelf_life_days': 90}
        )
        self.stdout.write(self.style.SUCCESS(f"  + Seeded Categories: Vegetables, Fruits, Grains"))

        # 4. Produce Listings
        today = timezone.now().date()
        products_data = [
            {
                'farmer': ramesh_profile,
                'category': cat_veg,
                'name': 'Fresh Hybrid Tomatoes',
                'variety': 'Abhinav 1057',
                'grade': Product.QualityGrade.GRADE_A,
                'available_quantity_kg': Decimal('500.00'),
                'minimum_order_kg': Decimal('5.00'),
                'farmer_base_price_per_kg': Decimal('25.00'),
                'traditional_market_price_per_kg': Decimal('42.00'),
                'harvest_date': today,
                'emoji_icon': '🍅',
                'image': 'products/fresh_tomatoes.jpg',
                'is_organic': True,
            },
            {
                'farmer': birsa_profile,
                'category': cat_veg,
                'name': 'Kufri Jyoti Potatoes',
                'variety': 'Kufri Jyoti',
                'grade': Product.QualityGrade.GRADE_A,
                'available_quantity_kg': Decimal('800.00'),
                'minimum_order_kg': Decimal('10.00'),
                'farmer_base_price_per_kg': Decimal('18.00'),
                'traditional_market_price_per_kg': Decimal('30.00'),
                'harvest_date': today,
                'emoji_icon': '🥔',
                'image': 'products/kufri_potatoes.jpg',
                'is_organic': False,
            },
            {
                'farmer': birsa_profile,
                'category': cat_veg,
                'name': 'Nashik Red Onions',
                'variety': 'Garwa High Shelf',
                'grade': Product.QualityGrade.GRADE_B,
                'available_quantity_kg': Decimal('600.00'),
                'minimum_order_kg': Decimal('5.00'),
                'farmer_base_price_per_kg': Decimal('28.00'),
                'traditional_market_price_per_kg': Decimal('45.00'),
                'harvest_date': today,
                'emoji_icon': '🧅',
                'image': 'products/nashik_onions.jpg',
                'is_organic': False,
            },
            {
                'farmer': sita_profile,
                'category': cat_veg,
                'name': 'Spicy Green Chillies',
                'variety': 'Jwala Light Green',
                'grade': Product.QualityGrade.GRADE_A,
                'available_quantity_kg': Decimal('150.00'),
                'minimum_order_kg': Decimal('2.00'),
                'farmer_base_price_per_kg': Decimal('60.00'),
                'traditional_market_price_per_kg': Decimal('95.00'),
                'harvest_date': today,
                'emoji_icon': '🌶️',
                'image': 'products/green_chillies.jpg',
                'is_organic': True,
            },
        ]

        for p_data in products_data:
            prod, _ = Product.objects.get_or_create(
                farmer=p_data['farmer'],
                name=p_data['name'],
                defaults=p_data
            )
            # Re-save to trigger price breakdown calculations
            prod.save()
            self.stdout.write(self.style.SUCCESS(f"  + Seeded Produce: {prod.name} ({prod.available_quantity_kg} kg @ Rs {prod.consumer_price_per_kg}/kg)"))

        # 5. Seed SMS Logs for Ramesh Kumar
        FarmerSMSLog.objects.get_or_create(
            farmer=ramesh_profile,
            alert_type=FarmerSMSLog.AlertType.PAYMENT_REMITTED,
            phone_number=ramesh_profile.user.phone,
            message_text="Aapke 400 kg Tamatar ka Rs 10,000 ka bhugtan aapke SBI khate me jama kar diya gaya hai. VDF: Sunil Mahto."
        )
        FarmerSMSLog.objects.get_or_create(
            farmer=ramesh_profile,
            alert_type=FarmerSMSLog.AlertType.LISTING_CREATED,
            phone_number=ramesh_profile.user.phone,
            message_text="Aapki 500 kg Hybrid Tamatar ki soochi Rs 25/kg ke bhav se AgriConnect par darj ho gayi hai."
        )
        FarmerSMSLog.objects.get_or_create(
            farmer=ramesh_profile,
            alert_type=FarmerSMSLog.AlertType.MARKET_ALERT,
            phone_number=ramesh_profile.user.phone,
            message_text="Mandi Suchna: Aaj Ranchi Mandi me tamatar modal rate Rs 22/kg hai. AgriConnect par aapko Rs 25/kg mil rahe hain."
        )
        self.stdout.write(self.style.SUCCESS("  + Seeded Simulated SMS Notifications"))

        self.stdout.write(self.style.SUCCESS("\nPhase 2 Seeding Complete!"))
