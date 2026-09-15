from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser

class Command(BaseCommand):
    help = "Seed initial demonstration accounts for all 5 roles (SIH Demo & Testing)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Phase 1 accounts..."))

        demo_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@agriconnect.org',
                'first_name': 'Aamir',
                'last_name': 'Admin',
                'phone': '9800000001',
                'role': CustomUser.Role.ADMIN,
                'village_or_city': 'Ranchi',
                'district': 'Ranchi',
                'state': 'Jharkhand',
                'pincode': '834001',
                'preferred_language': 'English',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            },
            {
                'username': 'vdf_sunil',
                'password': 'vdf123',
                'email': 'sunil.vdf@agriconnect.org',
                'first_name': 'Sunil',
                'last_name': 'Mahto',
                'phone': '9800000002',
                'role': CustomUser.Role.FACILITATOR,
                'village_or_city': 'Angara',
                'district': 'Ranchi',
                'state': 'Jharkhand',
                'pincode': '835103',
                'preferred_language': 'Hindi',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': True,
            },
            {
                'username': 'farmer_ramesh',
                'password': 'farmer123',
                'email': 'ramesh.farmer@agriconnect.org',
                'first_name': 'Ramesh',
                'last_name': 'Kumar',
                'phone': '9800000003',
                'role': CustomUser.Role.FARMER,
                'village_or_city': 'Jonha',
                'district': 'Ranchi',
                'state': 'Jharkhand',
                'pincode': '835103',
                'preferred_language': 'Hindi',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': True,
            },
            {
                'username': 'consumer_priya',
                'password': 'consumer123',
                'email': 'priya.sharma@gmail.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'phone': '9800000004',
                'role': CustomUser.Role.CONSUMER,
                'village_or_city': 'Morabadi, Ranchi',
                'district': 'Ranchi',
                'state': 'Jharkhand',
                'pincode': '834008',
                'preferred_language': 'English',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': True,
            },
            {
                'username': 'delivery_rajesh',
                'password': 'delivery123',
                'email': 'rajesh.logistics@agriconnect.org',
                'first_name': 'Rajesh',
                'last_name': 'Verma',
                'phone': '9800000005',
                'role': CustomUser.Role.DELIVERY,
                'village_or_city': 'Ranchi City Center',
                'district': 'Ranchi',
                'state': 'Jharkhand',
                'pincode': '834001',
                'preferred_language': 'Hindi',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': True,
            },
        ]

        created_count = 0
        updated_count = 0

        for user_data in demo_users:
            username = user_data['username']
            password = user_data.pop('password')

            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults=user_data
            )

            user.set_password(password)
            for key, val in user_data.items():
                setattr(user, key, val)
            user.save()

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + Created {user.role}: {username} (password: {password})"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"  ~ Updated {user.role}: {username} (password: {password})"))

        self.stdout.write(self.style.SUCCESS(f"\nPhase 1 Seeding Complete: {created_count} created, {updated_count} updated."))
        self.stdout.write(self.style.NOTICE("Quick Login Credentials:"))
        self.stdout.write("  - Administrator: admin / admin123")
        self.stdout.write("  - Facilitator (VDF): vdf_sunil / vdf123")
        self.stdout.write("  - Farmer: farmer_ramesh / farmer123")
        self.stdout.write("  - Consumer: consumer_priya / consumer123")
        self.stdout.write("  - Delivery Partner: delivery_rajesh / delivery123")
