from django.contrib import admin
from .models import Staff, CourtType, Court, Equipment, Customer, Booking, BookingEquipment, Penalty, Payment


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']


@admin.register(CourtType)
class CourtTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'hourly_rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['name', 'court_type', 'is_available']
    list_filter = ['court_type', 'is_available']
    search_fields = ['name']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'rental_fee', 'quantity_available', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at']
    search_fields = ['name', 'phone', 'email']


class BookingEquipmentInline(admin.TabularInline):
    model = BookingEquipment
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


class PenaltyInline(admin.TabularInline):
    model = Penalty
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'court', 'booking_date', 'start_time', 'end_time', 'status', 'total_amount']
    list_filter = ['status', 'booking_source', 'booking_date', 'court__court_type']
    search_fields = ['customer__name', 'customer__phone', 'court__name']
    date_hierarchy = 'booking_date'
    inlines = [BookingEquipmentInline, PaymentInline, PenaltyInline]


@admin.register(BookingEquipment)
class BookingEquipmentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'equipment', 'quantity', 'subtotal', 'returned']
    list_filter = ['returned', 'equipment']


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ['booking', 'penalty_type', 'amount', 'created_at']
    list_filter = ['penalty_type', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'payment_type', 'payment_method', 'amount', 'payment_date']
    list_filter = ['payment_type', 'payment_method', 'payment_date']


# Customize admin site
admin.site.site_header = "LOSIK Sports Arena Admin"
admin.site.site_title = "LOSIK Sports Arena"
admin.site.index_title = "Management Dashboard"
