from django import forms
from .models import FactPayment, Reservation


class FactPaymentForm(forms.ModelForm):
    class Meta:
        model = FactPayment
        fields = ('institution', 'kosgu', 'year', 'amount', 'payment_date', 'description', 'document_number')
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('institution', 'kosgu', 'year', 'contract_number', 'contractor',
                  'amount', 'contract_date', 'note')
        widgets = {
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }
