from django import forms
from .models import BudgetRequest, RequestLine


class BudgetRequestForm(forms.ModelForm):
    class Meta:
        model = BudgetRequest
        fields = ('period_year', 'period_type', 'period_quarter', 'funding_type', 'deadline')
        widgets = {
            'period_year': forms.NumberInput(attrs={'min': 2024, 'max': 2030}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }


class AdminBudgetRequestForm(BudgetRequestForm):
    """Форма для администратора: позволяет выбрать учреждение вручную."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.institutions.models import Institution
        self.fields['institution'] = forms.ModelChoiceField(
            queryset=Institution.objects.filter(is_active=True).order_by('short_name'),
            label='Учреждение',
        )
        # Ставим institution первым в порядке отображения
        field_order = ['institution'] + [f for f in self.fields if f != 'institution']
        self.fields = {k: self.fields[k] for k in field_order}


class RequestLineForm(forms.ModelForm):
    class Meta:
        model = RequestLine
        fields = ('kosgu', 'kvr', 'description', 'unit_price', 'quantity', 'attachment', 'note')
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'step': '0.001'}),
            'description': forms.TextInput(attrs={'placeholder': 'Например: Текущий ремонт системы отопления'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.classifiers.models import KOSGU, KVR
        self.fields['kosgu'].queryset = KOSGU.objects.filter(is_active=True)
        self.fields['kvr'].queryset = KVR.objects.filter(is_active=True)
        self.fields['kvr'].required = False


class ReviewForm(forms.Form):
    """Форма бухгалтера для согласования/отклонения заявки."""
    action = forms.ChoiceField(
        choices=[('approve', 'Согласовать'), ('return', 'Вернуть на доработку'), ('reject', 'Отклонить')],
        widget=forms.RadioSelect,
        label='Решение',
    )
    approved_amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        label='Согласованная сумма (оставьте пустым = по заявке)',
        widget=forms.NumberInput(attrs={'step': '0.01'}),
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Комментарий (обязателен при возврате/отклонении)',
    )
