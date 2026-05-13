from django.contrib import admin
from .models import Institution, BudgetLimit


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'institution_type', 'inn', 'is_active')
    list_filter = ('institution_type', 'is_active')
    search_fields = ('name', 'short_name', 'inn')


@admin.register(BudgetLimit)
class BudgetLimitAdmin(admin.ModelAdmin):
    list_display = ('institution', 'year', 'total_limit', 'set_by', 'set_at')
    list_filter = ('year',)
    autocomplete_fields = ('institution',)
