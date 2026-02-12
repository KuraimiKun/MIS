from django import forms
from django.forms import inlineformset_factory
from .models import Customer, Booking, BookingEquipment, Payment, Penalty, Court


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (optional)'
            }),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['court', 'booking_date', 'start_time', 'end_time', 
                  'duration_hours', 'booking_source', 'notes']
        widgets = {
            'court': forms.Select(attrs={'class': 'form-select'}),
            'booking_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'booking_source': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['court'].queryset = Court.objects.filter(
            is_available=True
        ).select_related('court_type')


class BookingEquipmentForm(forms.ModelForm):
    class Meta:
        model = BookingEquipment
        fields = ['equipment', 'quantity']
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
        }


BookingEquipmentFormSet = inlineformset_factory(
    Booking, 
    BookingEquipment, 
    form=BookingEquipmentForm,
    extra=3,
    can_delete=True
)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_type', 'payment_method', 'amount', 'notes']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Payment notes...'
            }),
        }


class PenaltyForm(forms.ModelForm):
    class Meta:
        model = Penalty
        fields = ['penalty_type', 'amount', 'description']
        widgets = {
            'penalty_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the reason for penalty...'
            }),
        }
