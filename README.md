# LOSIK Sports Arena Management System

A comprehensive web-based management system for LOSIK Sports Arena, built with Django. This system streamlines court bookings, equipment rentals, payment processing, and customer management for sports facilities.

## 📋 Features

### Core Functionality
- **Court Management**: Manage multiple court types (Badminton, Basketball, etc.) with individual court tracking
- **Booking System**: Complete reservation system with date/time scheduling and conflict prevention
- **Customer Management**: Track customer information and booking history
- **Equipment Rental**: Manage sports equipment inventory and rentals
- **Payment Processing**: Support for down payments (50%) and final payments with multiple payment methods (Cash, Bank Transfer, QRIS)
- **Penalty Management**: Track and apply penalties for late returns, equipment damage, and overtime
- **Receipt Generation**: Automatic receipt generation for all transactions
- **Dashboard & Reports**: Real-time analytics and comprehensive reporting

### User Roles
- **Admin**: Full system access and administrative functions
- **Field Officer**: Manage bookings, payments, and day-to-day operations
- **Owner**: View reports and analytics

### Booking Workflow
1. Customer booking (Walk-in or WhatsApp)
2. Down payment collection (50%)
3. Booking confirmation
4. Court usage (Active status)
5. Final payment and completion
6. Equipment return tracking

## 🛠️ Technology Stack

- **Framework**: Django 5.1.2
- **Database**: SQLite3 (development)
- **Frontend**: HTML, CSS, Django Templates
- **Python**: 3.x

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MIS
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Set up initial data**
   ```bash
   python manage.py setup_initial_data
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📂 Project Structure

```
MIS/
├── core/                           # Main application
│   ├── management/                 # Custom management commands
│   │   └── commands/
│   │       └── setup_initial_data.py
│   ├── migrations/                 # Database migrations
│   ├── templatetags/              # Custom template tags
│   ├── admin.py                   # Admin configurations
│   ├── forms.py                   # Form definitions
│   ├── models.py                  # Database models
│   ├── urls.py                    # URL routing
│   └── views.py                   # View logic
├── losik_arena/                   # Project settings
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Main URL configuration
│   └── wsgi.py                    # WSGI configuration
├── static/                        # Static files (CSS, JS, images)
│   └── css/
│       └── style.css
├── templates/                     # HTML templates
│   ├── base.html                  # Base template
│   └── core/                      # App-specific templates
│       ├── dashboard.html
│       ├── booking_list.html
│       ├── booking_form.html
│       ├── court_schedule.html
│       ├── customer_list.html
│       ├── equipment_list.html
│       ├── payment_form.html
│       ├── receipt.html
│       └── reports.html
├── screenshots/                   # Application screenshots
├── manage.py                      # Django management script
├── db.sqlite3                     # SQLite database
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 📊 Database Models

- **Staff**: System users with different roles
- **CourtType**: Types of courts available (with hourly rates)
- **Court**: Individual courts for booking
- **Equipment**: Rental equipment inventory
- **Customer**: Customer information
- **Booking**: Court reservations and bookings
- **BookingEquipment**: Equipment rented with bookings
- **Penalty**: Penalties applied to bookings
- **Payment**: Payment records and transactions

## 🖼️ Screenshots

Screenshots of the application are available in the [`screenshots/`](screenshots/) folder:

- Dashboard view
- Booking management
- Court schedule
- Customer management
- Payment processing
- Equipment rental
- Receipt generation
- Reports and analytics

*Note: Add your screenshots to the `screenshots/` folder to document the application interface.*

## 🚀 Usage

### Creating a Booking
1. Navigate to "New Booking"
2. Select or create a customer
3. Choose court type and specific court
4. Set date, start time, and duration
5. Add equipment rentals (optional)
6. Process down payment (50%)
7. Generate booking receipt

### Processing Payments
1. View booking details
2. Select "Add Payment"
3. Choose payment type (Down Payment/Final Payment)
4. Select payment method
5. Enter amount and confirm
6. Generate receipt

### Managing Equipment
1. Track equipment inventory
2. Mark equipment as rented/returned
3. Apply penalties for late returns or damage

### Generating Reports
- Access the Reports section from the dashboard
- View bookings by date range
- Analyze revenue and payment statistics
- Track equipment utilization

## 🔐 Security Notes

- Change the `SECRET_KEY` in `settings.py` for production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use environment variables for sensitive data
- Implement proper database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software for LOSIK Sports Arena.

## 📧 Contact

For support or inquiries, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Django Version**: 5.1.2
