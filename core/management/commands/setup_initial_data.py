from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import CourtType, Court, Equipment, Staff
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial data for LOSIK Sports Arena'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')

        # Create court types with pricing from requirements
        court_types_data = [
            {'name': 'Indoor Badminton', 'hourly_rate': Decimal('60000.00'), 'description': 'Indoor badminton court with proper lighting'},
            {'name': 'Indoor Basketball', 'hourly_rate': Decimal('120000.00'), 'description': 'Full-size indoor basketball court'},
            {'name': 'Indoor Tennis', 'hourly_rate': Decimal('150000.00'), 'description': 'Indoor tennis court with air conditioning'},
            {'name': 'Outdoor Tennis', 'hourly_rate': Decimal('90000.00'), 'description': 'Outdoor tennis court with proper drainage'},
        ]

        for ct_data in court_types_data:
            court_type, created = CourtType.objects.get_or_create(
                name=ct_data['name'],
                defaults={
                    'hourly_rate': ct_data['hourly_rate'],
                    'description': ct_data['description']
                }
            )
            if created:
                self.stdout.write(f'  Created court type: {court_type.name}')
            else:
                self.stdout.write(f'  Court type already exists: {court_type.name}')

        # Create individual courts
        courts_data = [
            {'name': 'Badminton Court 1', 'type': 'Indoor Badminton'},
            {'name': 'Badminton Court 2', 'type': 'Indoor Badminton'},
            {'name': 'Badminton Court 3', 'type': 'Indoor Badminton'},
            {'name': 'Basketball Court 1', 'type': 'Indoor Basketball'},
            {'name': 'Basketball Court 2', 'type': 'Indoor Basketball'},
            {'name': 'Indoor Tennis Court 1', 'type': 'Indoor Tennis'},
            {'name': 'Indoor Tennis Court 2', 'type': 'Indoor Tennis'},
            {'name': 'Outdoor Tennis Court 1', 'type': 'Outdoor Tennis'},
            {'name': 'Outdoor Tennis Court 2', 'type': 'Outdoor Tennis'},
        ]

        for court_data in courts_data:
            court_type = CourtType.objects.get(name=court_data['type'])
            court, created = Court.objects.get_or_create(
                name=court_data['name'],
                defaults={'court_type': court_type}
            )
            if created:
                self.stdout.write(f'  Created court: {court.name}')
            else:
                self.stdout.write(f'  Court already exists: {court.name}')

        # Create equipment with pricing from requirements
        equipment_data = [
            {'name': 'Shuttlecock', 'rental_fee': Decimal('10000.00'), 'quantity': 50, 'description': 'Badminton shuttlecock'},
            {'name': 'Tennis Ball', 'rental_fee': Decimal('10000.00'), 'quantity': 30, 'description': 'Tennis ball'},
            {'name': 'Basketball', 'rental_fee': Decimal('20000.00'), 'quantity': 10, 'description': 'Standard basketball'},
            {'name': 'Badminton Racket', 'rental_fee': Decimal('25000.00'), 'quantity': 20, 'description': 'Badminton racket'},
            {'name': 'Tennis Racket', 'rental_fee': Decimal('25000.00'), 'quantity': 15, 'description': 'Tennis racket'},
        ]

        for eq_data in equipment_data:
            equipment, created = Equipment.objects.get_or_create(
                name=eq_data['name'],
                defaults={
                    'rental_fee': eq_data['rental_fee'],
                    'quantity_available': eq_data['quantity'],
                    'description': eq_data['description']
                }
            )
            if created:
                self.stdout.write(f'  Created equipment: {equipment.name}')
            else:
                self.stdout.write(f'  Equipment already exists: {equipment.name}')

        # Create admin superuser if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@losik.com',
                password='admin123',
                first_name='Admin',
                last_name='LOSIK'
            )
            Staff.objects.create(user=admin_user, role='owner', phone='081234567890')
            self.stdout.write(self.style.SUCCESS('  Created admin superuser (username: admin, password: admin123)'))
        else:
            self.stdout.write('  Admin user already exists')

        # Create sample staff users
        staff_data = [
            {'username': 'admin1', 'first_name': 'Budi', 'last_name': 'Santoso', 'role': 'admin', 'phone': '081234567891'},
            {'username': 'admin2', 'first_name': 'Siti', 'last_name': 'Rahayu', 'role': 'admin', 'phone': '081234567892'},
            {'username': 'admin3', 'first_name': 'Andi', 'last_name': 'Wijaya', 'role': 'admin', 'phone': '081234567893'},
            {'username': 'field1', 'first_name': 'Joko', 'last_name': 'Prasetyo', 'role': 'field', 'phone': '081234567894'},
            {'username': 'field2', 'first_name': 'Agus', 'last_name': 'Susanto', 'role': 'field', 'phone': '081234567895'},
        ]

        for staff_info in staff_data:
            if not User.objects.filter(username=staff_info['username']).exists():
                user = User.objects.create_user(
                    username=staff_info['username'],
                    password='password123',
                    first_name=staff_info['first_name'],
                    last_name=staff_info['last_name']
                )
                Staff.objects.create(
                    user=user, 
                    role=staff_info['role'], 
                    phone=staff_info['phone']
                )
                self.stdout.write(f'  Created staff: {user.get_full_name()} ({staff_info["role"]})')
            else:
                self.stdout.write(f'  Staff already exists: {staff_info["username"]}')

        self.stdout.write(self.style.SUCCESS('\nInitial data setup complete!'))
        self.stdout.write(self.style.SUCCESS('You can login with:'))
        self.stdout.write(self.style.SUCCESS('  - Username: admin, Password: admin123 (Owner)'))
        self.stdout.write(self.style.SUCCESS('  - Username: admin1/admin2/admin3, Password: password123 (Admin Staff)'))
