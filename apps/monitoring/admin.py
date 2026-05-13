from django.contrib import admin
from .models import FactPayment, Reservation


@admin.register(FactPayment)
class FactPaymentAdmin(admin.ModelAdmin):
    list_display = ('institution', 'kosgu', 'year', 'amount', 'payment_date', 'added_by')
    list_filter = ('year', 'institution')
    search_fields = ('institution__short_name', 'description', 'document_number')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'contract_number', 'contractor', 'amount', 'status', 'contract_date')
    list_filter = ('status', 'year', 'institution')
    search_fields = ('contract_number', 'contractor', 'institution__short_name')
