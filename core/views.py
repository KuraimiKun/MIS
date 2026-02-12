from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import json

from .models import (
    Staff, CourtType, Court, Equipment, Customer, 
    Booking, BookingEquipment, Penalty, Payment
)
from .forms import (
    BookingForm, CustomerForm, PaymentForm, 
    BookingEquipmentFormSet, PenaltyForm
)


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard with statistics and charts"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Today's bookings
    todays_bookings = Booking.objects.filter(booking_date=today).exclude(status='cancelled')
    
    # Revenue statistics
    monthly_revenue = Payment.objects.filter(
        payment_date__date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    daily_revenue = Payment.objects.filter(
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Booking statistics
    total_bookings_today = todays_bookings.count()
    active_bookings = Booking.objects.filter(status='active').count()
    pending_bookings = Booking.objects.filter(status__in=['pending', 'confirmed']).count()
    
    # Court availability
    courts = Court.objects.filter(is_available=True).select_related('court_type')
    court_availability = []
    
    current_time = timezone.now().time()
    for court in courts:
        current_booking = Booking.objects.filter(
            court=court,
            booking_date=today,
            start_time__lte=current_time,
            end_time__gte=current_time,
            status__in=['confirmed', 'active']
        ).first()
        
        court_availability.append({
            'court': court,
            'is_occupied': current_booking is not None,
            'current_booking': current_booking
        })
    
    # Revenue trend (last 7 days)
    last_7_days = today - timedelta(days=6)
    revenue_trend = Payment.objects.filter(
        payment_date__date__gte=last_7_days
    ).annotate(
        date=TruncDate('payment_date')
    ).values('date').annotate(
        total=Sum('amount')
    ).order_by('date')
    
    revenue_trend_labels = []
    revenue_trend_data = []
    for i in range(7):
        day = last_7_days + timedelta(days=i)
        revenue_trend_labels.append(day.strftime('%d %b'))
        day_revenue = next(
            (item['total'] for item in revenue_trend if item['date'] == day), 
            Decimal('0')
        )
        revenue_trend_data.append(float(day_revenue))
    
    # Booking by court type
    bookings_by_court_type = Booking.objects.filter(
        booking_date__gte=start_of_month
    ).exclude(status='cancelled').values(
        'court__court_type__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    court_type_labels = [item['court__court_type__name'] for item in bookings_by_court_type]
    court_type_data = [item['count'] for item in bookings_by_court_type]
    
    # Equipment usage
    equipment_usage = BookingEquipment.objects.filter(
        booking__booking_date__gte=start_of_month
    ).values('equipment__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related(
        'customer', 'court', 'court__court_type'
    ).order_by('-created_at')[:10]
    
    context = {
        'todays_bookings': todays_bookings,
        'monthly_revenue': monthly_revenue,
        'daily_revenue': daily_revenue,
        'total_bookings_today': total_bookings_today,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'court_availability': court_availability,
        'revenue_trend_labels': json.dumps(revenue_trend_labels),
        'revenue_trend_data': json.dumps(revenue_trend_data),
        'court_type_labels': json.dumps(court_type_labels),
        'court_type_data': json.dumps(court_type_data),
        'equipment_usage': equipment_usage,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def booking_list(request):
    """List all bookings with filtering"""
    bookings = Booking.objects.select_related(
        'customer', 'court', 'court__court_type', 'created_by'
    ).order_by('-booking_date', '-start_time')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by date
    date_filter = request.GET.get('date')
    if date_filter:
        bookings = bookings.filter(booking_date=date_filter)
    
    # Filter by court type
    court_type = request.GET.get('court_type')
    if court_type:
        bookings = bookings.filter(court__court_type_id=court_type)
    
    # Search
    search = request.GET.get('search')
    if search:
        bookings = bookings.filter(
            Q(customer__name__icontains=search) | 
            Q(customer__phone__icontains=search)
        )
    
    court_types = CourtType.objects.filter(is_active=True)
    
    context = {
        'bookings': bookings,
        'court_types': court_types,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'core/booking_list.html', context)


@login_required
def booking_create(request):
    """Create a new booking"""
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, prefix='customer')
        booking_form = BookingForm(request.POST, prefix='booking')
        
        # Check if existing customer
        existing_customer_id = request.POST.get('existing_customer')
        
        if existing_customer_id:
            customer = get_object_or_404(Customer, pk=existing_customer_id)
            customer_valid = True
        else:
            customer_valid = customer_form.is_valid()
            if customer_valid:
                customer = customer_form.save()
        
        if customer_valid and booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.customer = customer
            booking.created_by = request.user
            
            # Calculate court rental fee
            duration = booking.duration_hours
            booking.court_rental_fee = booking.court.court_type.hourly_rate * duration
            booking.save()
            
            # Handle equipment
            equipment_data = request.POST.getlist('equipment')
            quantities = request.POST.getlist('equipment_quantity')
            
            total_equipment_fee = Decimal('0')
            for i, equip_id in enumerate(equipment_data):
                if equip_id:
                    equipment = Equipment.objects.get(pk=equip_id)
                    qty = int(quantities[i]) if i < len(quantities) and quantities[i] else 1
                    
                    BookingEquipment.objects.create(
                        booking=booking,
                        equipment=equipment,
                        quantity=qty,
                        unit_price=equipment.rental_fee,
                        subtotal=equipment.rental_fee * qty
                    )
                    total_equipment_fee += equipment.rental_fee * qty
            
            # Update booking with equipment fee
            booking.equipment_rental_fee = total_equipment_fee
            booking.save()
            
            messages.success(request, f'Booking #{booking.id} created successfully!')
            return redirect('booking_detail', pk=booking.pk)
    else:
        customer_form = CustomerForm(prefix='customer')
        booking_form = BookingForm(prefix='booking')
    
    customers = Customer.objects.all().order_by('-created_at')[:50]
    equipment_list = Equipment.objects.filter(is_active=True)
    courts = Court.objects.filter(is_available=True).select_related('court_type')
    
    context = {
        'customer_form': customer_form,
        'booking_form': booking_form,
        'customers': customers,
        'equipment_list': equipment_list,
        'courts': courts,
    }
    return render(request, 'core/booking_form.html', context)


@login_required
def booking_detail(request, pk):
    """View booking details"""
    booking = get_object_or_404(
        Booking.objects.select_related(
            'customer', 'court', 'court__court_type', 'created_by'
        ).prefetch_related('equipment_rentals__equipment', 'payments', 'penalties'),
        pk=pk
    )
    
    context = {
        'booking': booking,
    }
    return render(request, 'core/booking_detail.html', context)


@login_required
def booking_update_status(request, pk):
    """Update booking status"""
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking status updated to {booking.get_status_display()}')
    
    return redirect('booking_detail', pk=pk)


@login_required
def add_payment(request, booking_id):
    """Add payment to a booking"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.received_by = request.user
            payment.save()
            messages.success(request, f'Payment of Rp {payment.amount:,.0f} recorded successfully!')
            return redirect('booking_detail', pk=booking_id)
    else:
        # Suggest down payment or remaining amount
        if booking.status == 'pending':
            suggested_amount = booking.calculate_down_payment()
            payment_type = 'down_payment'
        else:
            suggested_amount = booking.remaining_payment
            payment_type = 'final_payment'
        
        form = PaymentForm(initial={
            'amount': suggested_amount,
            'payment_type': payment_type
        })
    
    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'core/payment_form.html', context)


@login_required
def add_penalty(request, booking_id):
    """Add penalty to a booking"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if request.method == 'POST':
        form = PenaltyForm(request.POST)
        if form.is_valid():
            penalty = form.save(commit=False)
            penalty.booking = booking
            penalty.created_by = request.user
            penalty.save()
            messages.success(request, f'Penalty of Rp {penalty.amount:,.0f} added!')
            return redirect('booking_detail', pk=booking_id)
    else:
        form = PenaltyForm()
    
    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'core/penalty_form.html', context)


@login_required
def return_equipment(request, booking_id, equipment_id):
    """Mark equipment as returned"""
    booking_equipment = get_object_or_404(
        BookingEquipment, 
        booking_id=booking_id, 
        pk=equipment_id
    )
    
    booking_equipment.returned = True
    booking_equipment.returned_at = timezone.now()
    booking_equipment.save()
    
    messages.success(request, f'{booking_equipment.equipment.name} marked as returned.')
    return redirect('booking_detail', pk=booking_id)


@login_required
def court_schedule(request):
    """View court schedule/availability"""
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()
    
    courts = Court.objects.filter(is_available=True).select_related('court_type')
    
    # Generate time slots (07:00 to 23:00)
    time_slots = []
    for hour in range(7, 23):
        time_slots.append(time(hour, 0))
    
    # Get bookings for selected date
    bookings = Booking.objects.filter(
        booking_date=selected_date,
        status__in=['confirmed', 'active', 'completed']
    ).select_related('customer', 'court')
    
    # Build schedule matrix
    schedule = {}
    for court in courts:
        schedule[court.id] = {}
        for slot in time_slots:
            booking = next(
                (b for b in bookings 
                 if b.court_id == court.id 
                 and b.start_time <= slot < b.end_time),
                None
            )
            schedule[court.id][slot] = booking
    
    context = {
        'courts': courts,
        'time_slots': time_slots,
        'schedule': schedule,
        'selected_date': selected_date,
    }
    return render(request, 'core/court_schedule.html', context)


@login_required
def customer_list(request):
    """List all customers"""
    customers = Customer.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(name__icontains=search) | Q(phone__icontains=search)
        )
    
    context = {
        'customers': customers,
    }
    return render(request, 'core/customer_list.html', context)


@login_required
def customer_detail(request, pk):
    """View customer details and booking history"""
    customer = get_object_or_404(Customer, pk=pk)
    bookings = customer.bookings.select_related(
        'court', 'court__court_type'
    ).order_by('-booking_date')
    
    total_spent = customer.bookings.filter(
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    context = {
        'customer': customer,
        'bookings': bookings,
        'total_spent': total_spent,
    }
    return render(request, 'core/customer_detail.html', context)


@login_required
def equipment_list(request):
    """List all equipment"""
    equipment = Equipment.objects.all()
    
    # Equipment usage stats
    for item in equipment:
        item.times_rented = BookingEquipment.objects.filter(
            equipment=item
        ).aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'equipment': equipment,
    }
    return render(request, 'core/equipment_list.html', context)


@login_required
def reports(request):
    """Generate various reports"""
    # Date range
    end_date = timezone.now().date()
    start_date = end_date.replace(day=1)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Revenue report
    revenue_data = Payment.objects.filter(
        payment_date__date__gte=start_date,
        payment_date__date__lte=end_date
    ).aggregate(
        total_revenue=Sum('amount'),
        total_transactions=Count('id')
    )
    
    # Revenue by payment method
    revenue_by_method = Payment.objects.filter(
        payment_date__date__gte=start_date,
        payment_date__date__lte=end_date
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Revenue by court type
    court_revenue = Booking.objects.filter(
        booking_date__gte=start_date,
        booking_date__lte=end_date,
        status='completed'
    ).values('court__court_type__name').annotate(
        total=Sum('court_rental_fee'),
        count=Count('id')
    ).order_by('-total')
    
    # Equipment revenue
    equipment_revenue = BookingEquipment.objects.filter(
        booking__booking_date__gte=start_date,
        booking__booking_date__lte=end_date,
        booking__status='completed'
    ).values('equipment__name').annotate(
        total=Sum('subtotal'),
        quantity=Sum('quantity')
    ).order_by('-total')
    
    # Monthly trend
    monthly_revenue = Payment.objects.filter(
        payment_date__date__gte=start_date - timedelta(days=365),
        payment_date__date__lte=end_date
    ).annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    monthly_labels = [item['month'].strftime('%b %Y') for item in monthly_revenue]
    monthly_data = [float(item['total']) for item in monthly_revenue]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'revenue_data': revenue_data,
        'revenue_by_method': revenue_by_method,
        'court_revenue': court_revenue,
        'equipment_revenue': equipment_revenue,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
    }
    return render(request, 'core/reports.html', context)


@login_required
def print_receipt(request, booking_id):
    """Generate printable receipt"""
    booking = get_object_or_404(
        Booking.objects.select_related(
            'customer', 'court', 'court__court_type'
        ).prefetch_related('equipment_rentals__equipment', 'payments', 'penalties'),
        pk=booking_id
    )
    
    context = {
        'booking': booking,
    }
    return render(request, 'core/receipt.html', context)


# API Views for AJAX
@login_required
def api_check_availability(request):
    """Check court availability for a specific date and time"""
    court_id = request.GET.get('court_id')
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    
    if not all([court_id, date, start_time, end_time]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    # Check for overlapping bookings
    overlapping = Booking.objects.filter(
        court_id=court_id,
        booking_date=date,
        status__in=['pending', 'confirmed', 'active']
    ).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    ).exists()
    
    return JsonResponse({
        'available': not overlapping,
        'message': 'Court is available' if not overlapping else 'Court is already booked for this time slot'
    })


@login_required
def api_get_court_price(request):
    """Get court hourly price"""
    court_id = request.GET.get('court_id')
    
    if not court_id:
        return JsonResponse({'error': 'Missing court_id'}, status=400)
    
    court = get_object_or_404(Court, pk=court_id)
    
    return JsonResponse({
        'hourly_rate': float(court.court_type.hourly_rate),
        'court_type': court.court_type.name
    })


@login_required
def api_search_customer(request):
    """Search customers by name or phone"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'customers': []})
    
    customers = Customer.objects.filter(
        Q(name__icontains=query) | Q(phone__icontains=query)
    )[:10]
    
    data = [{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email
    } for c in customers]
    
    return JsonResponse({'customers': data})
