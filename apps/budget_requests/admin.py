from django.contrib import admin
from .models import BudgetRequest, RequestLine, RequestLineLog


class RequestLineInline(admin.TabularInline):
    model = RequestLine
    extra = 0
    readonly_fields = ('amount',)


@admin.register(BudgetRequest)
class BudgetRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'institution', 'period_year', 'status', 'total_amount', 'approved_amount')
    list_filter = ('status', 'period_year', 'institution')
    search_fields = ('institution__short_name',)
    readonly_fields = ('total_amount', 'created_at', 'submitted_at', 'reviewed_at')
    inlines = [RequestLineInline]


@admin.register(RequestLineLog)
class RequestLineLogAdmin(admin.ModelAdmin):
    list_display = ('line', 'changed_by', 'old_amount', 'new_amount', 'changed_at')
    readonly_fields = ('changed_at',)
