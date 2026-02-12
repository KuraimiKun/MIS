from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Staff(models.Model):
    """Staff members of LOSIK Sports Arena"""
    ROLE_CHOICES = [
        ('admin', 'Administrative Staff'),
        ('field', 'Field Officer'),
        ('owner', 'Owner'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    class Meta:
        verbose_name_plural = "Staff"


class CourtType(models.Model):
    """Types of courts available for rental"""
    name = models.CharField(max_length=100)  # e.g., Indoor Badminton, Indoor Basketball
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)  # Price per hour
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - Rp {self.hourly_rate:,.0f}/hour"


class Court(models.Model):
    """Individual courts available for booking"""
    court_type = models.ForeignKey(CourtType, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=100)  # e.g., Badminton Court 1, Badminton Court 2
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.court_type.name})"


class Equipment(models.Model):
    """Sports equipment available for rental"""
    name = models.CharField(max_length=100)  # e.g., Badminton Racket, Shuttlecock
    rental_fee = models.DecimalField(max_digits=10, decimal_places=2)  # Fee per unit
    quantity_available = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - Rp {self.rental_fee:,.0f}/unit"


class Customer(models.Model):
    """Customer information"""
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.phone}"


class Booking(models.Model):
    """Court booking/reservation"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed (Down Payment Received)'),
        ('active', 'Active (In Use)'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('walk_in', 'Walk-in'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    court_rental_fee = models.DecimalField(max_digits=10, decimal_places=2)
    equipment_rental_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='walk_in')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bookings_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True)
    
    def calculate_court_fee(self):
        """Calculate court rental fee based on duration"""
        return self.court.court_type.hourly_rate * self.duration_hours
    
    def calculate_total(self):
        """Calculate total amount including equipment and penalties"""
        return self.court_rental_fee + self.equipment_rental_fee + self.penalty_fee
    
    def calculate_down_payment(self):
        """Calculate 50% down payment"""
        return self.total_amount * Decimal('0.5')
    
    def save(self, *args, **kwargs):
        if not self.court_rental_fee:
            self.court_rental_fee = self.calculate_court_fee()
        self.total_amount = self.calculate_total()
        self.remaining_payment = self.total_amount - self.down_payment
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.customer.name} - {self.court.name} - {self.booking_date}"
    
    class Meta:
        ordering = ['-booking_date', '-start_time']


class BookingEquipment(models.Model):
    """Equipment rented as part of a booking"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='equipment_rentals')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    returned = models.BooleanField(default=False)
    returned_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.equipment.rental_fee
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.equipment.name} x{self.quantity} for Booking #{self.booking.id}"


class Penalty(models.Model):
    """Penalties for late return or equipment damage"""
    PENALTY_TYPE_CHOICES = [
        ('late_return', 'Late Equipment Return'),
        ('equipment_damage', 'Equipment Damage'),
        ('overtime', 'Court Overtime'),
        ('other', 'Other'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='penalties')
    penalty_type = models.CharField(max_length=20, choices=PENALTY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update booking penalty fee
        total_penalties = self.booking.penalties.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        self.booking.penalty_fee = total_penalties
        self.booking.save()
    
    def __str__(self):
        return f"{self.get_penalty_type_display()} - Rp {self.amount:,.0f} for Booking #{self.booking.id}"
    
    class Meta:
        verbose_name_plural = "Penalties"


class Payment(models.Model):
    """Payment records for bookings"""
    PAYMENT_TYPE_CHOICES = [
        ('down_payment', 'Down Payment (50%)'),
        ('final_payment', 'Final Payment'),
        ('penalty_payment', 'Penalty Payment'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('qris', 'QRIS'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update booking payment status
        total_paid = self.booking.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        self.booking.down_payment = total_paid
        self.booking.remaining_payment = self.booking.total_amount - total_paid
        
        if total_paid >= self.booking.total_amount:
            if self.booking.status == 'active':
                self.booking.status = 'completed'
        elif total_paid >= self.booking.calculate_down_payment():
            if self.booking.status == 'pending':
                self.booking.status = 'confirmed'
        
        self.booking.save()
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - Rp {self.amount:,.0f} for Booking #{self.booking.id}"
