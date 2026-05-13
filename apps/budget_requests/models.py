from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class RequestStatus(models.TextChoices):
    """Жизненный цикл бюджетной заявки."""
    DRAFT = 'draft', 'Черновик'
    SUBMITTED = 'submitted', 'На проверке в ЦБ'
    RETURNED = 'returned', 'Возвращено на доработку'
    APPROVED = 'approved', 'Согласована'
    REJECTED = 'rejected', 'Отклонена'
    INCLUDED = 'included', 'Включена в бюджет'


class PeriodType(models.TextChoices):
    ANNUAL = 'annual', 'Годовая'
    QUARTERLY = 'quarterly', 'Квартальная'


class FundingType(models.TextChoices):
    SUBSIDY = 'subsidy', 'Субсидия на выполнение задания'
    PAID = 'paid', 'Платные услуги'
    OTHER = 'other', 'Иные цели'


STATUS_COLORS = {
    RequestStatus.DRAFT: 'secondary',
    RequestStatus.SUBMITTED: 'warning',
    RequestStatus.RETURNED: 'danger',
    RequestStatus.APPROVED: 'success',
    RequestStatus.REJECTED: 'danger',
    RequestStatus.INCLUDED: 'primary',
}


class BudgetRequest(models.Model):
    """Бюджетная заявка учреждения на финансирование."""

    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name='Учреждение',
    )
    period_year = models.PositiveSmallIntegerField(verbose_name='Год планирования')
    period_type = models.CharField(
        max_length=10,
        choices=PeriodType.choices,
        default=PeriodType.ANNUAL,
        verbose_name='Тип периода',
    )
    period_quarter = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(1, 'I кв.'), (2, 'II кв.'), (3, 'III кв.'), (4, 'IV кв.')],
        verbose_name='Квартал',
    )
    funding_type = models.CharField(
        max_length=10,
        choices=FundingType.choices,
        default=FundingType.SUBSIDY,
        verbose_name='Тип средств',
    )
    status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.DRAFT,
        verbose_name='Статус',
    )
    # Суммы
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Заявленная сумма (руб.)',
    )
    approved_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Согласованная сумма (руб.)',
    )
    # Авторство и даты
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_requests',
        verbose_name='Создана пользователем',
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        verbose_name='Проверил бухгалтер',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата проверки')
    # Дедлайн подачи
    deadline = models.DateField(null=True, blank=True, verbose_name='Срок подачи')
    comment = models.TextField(blank=True, verbose_name='Комментарий бухгалтера')

    class Meta:
        verbose_name = 'Бюджетная заявка'
        verbose_name_plural = 'Бюджетные заявки'
        ordering = ['-created_at']

    def __str__(self) -> str:
        period = f'{self.period_year}'
        if self.period_type == PeriodType.QUARTERLY and self.period_quarter:
            period += f' / {self.get_period_quarter_display()}'
        return f'Заявка #{self.pk} — {self.institution.short_name} ({period})'

    @property
    def status_color(self) -> str:
        return STATUS_COLORS.get(self.status, 'secondary')

    def recalculate_total(self) -> None:
        """Пересчитывает итоговую сумму из строк заявки."""
        total = self.lines.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def check_limit(self) -> bool:
        """Возвращает True, если заявка не превышает лимит учреждения."""
        try:
            limit = self.institution.limits.get(year=self.period_year)
            return self.total_amount <= limit.total_limit
        except Exception:
            return True  # Если лимит не установлен — не блокируем


def attachment_upload_path(instance: 'RequestLine', filename: str) -> str:
    return f'attachments/{instance.request.institution_id}/{instance.request_id}/{filename}'


class RequestLine(models.Model):
    """Строка расхода в бюджетной заявке."""

    request = models.ForeignKey(
        BudgetRequest,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Заявка',
    )
    kosgu = models.ForeignKey(
        'classifiers.KOSGU',
        on_delete=models.PROTECT,
        verbose_name='КОСГУ',
    )
    kvr = models.ForeignKey(
        'classifiers.KVR',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='КВР',
    )
    description = models.CharField(max_length=500, verbose_name='Детализация / Обоснование')
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Цена за ед. (руб.)',
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('1.000'),
        verbose_name='Количество',
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Итого (руб.)',
        editable=False,
    )
    attachment = models.FileField(
        upload_to=attachment_upload_path,
        null=True,
        blank=True,
        verbose_name='Файл-обоснование (скан/КП)',
    )
    note = models.TextField(blank=True, verbose_name='Примечание')

    class Meta:
        verbose_name = 'Строка заявки'
        verbose_name_plural = 'Строки заявки'

    def save(self, *args, **kwargs) -> None:
        # Автоматический расчёт суммы
        self.amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Обновляем итог заявки
        self.request.recalculate_total()

    def delete(self, *args, **kwargs) -> None:
        request = self.request
        super().delete(*args, **kwargs)
        request.recalculate_total()

    def __str__(self) -> str:
        return f'{self.kosgu} | {self.description[:50]} | {self.amount} руб.'


class RequestLineLog(models.Model):
    """
    Лог изменений суммы строки заявки.
    Фиксирует: кто, когда и как изменил сумму.
    """

    line = models.ForeignKey(
        RequestLine,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Строка заявки',
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Изменил',
    )
    old_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Было')
    new_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Стало')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    comment = models.TextField(blank=True, verbose_name='Причина изменения')

    class Meta:
        verbose_name = 'Лог изменения строки'
        verbose_name_plural = 'Логи изменений строк'
        ordering = ['-changed_at']

    def __str__(self) -> str:
        return f'Лог #{self.pk}: {self.old_amount} → {self.new_amount}'
