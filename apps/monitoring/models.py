from django.db import models
from django.contrib.auth.models import User


class FactPayment(models.Model):
    """Фактическое кассовое исполнение (оплаченные счета)."""

    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='fact_payments',
        verbose_name='Учреждение',
    )
    kosgu = models.ForeignKey(
        'classifiers.KOSGU',
        on_delete=models.PROTECT,
        verbose_name='КОСГУ',
    )
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма (руб.)')
    payment_date = models.DateField(verbose_name='Дата платежа')
    description = models.CharField(max_length=500, verbose_name='Назначение платежа')
    document_number = models.CharField(max_length=50, blank=True, verbose_name='Номер документа')
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Добавил',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Кассовый расход'
        verbose_name_plural = 'Кассовые расходы'
        ordering = ['-payment_date']

    def __str__(self) -> str:
        return f'{self.institution.short_name} | {self.kosgu.code} | {self.amount} руб. ({self.payment_date})'


class Reservation(models.Model):
    """
    Бронирование бюджетных средств под заключённый договор.
    Переводит сумму из «Свободного лимита» в «Зарезервировано».
    """

    class ReservationStatus(models.TextChoices):
        ACTIVE = 'active', 'Активно'
        CLOSED = 'closed', 'Закрыто (оплачено)'
        CANCELLED = 'cancelled', 'Отменено'

    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Учреждение',
    )
    kosgu = models.ForeignKey(
        'classifiers.KOSGU',
        on_delete=models.PROTECT,
        verbose_name='КОСГУ',
    )
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    contract_number = models.CharField(max_length=100, verbose_name='Номер договора')
    contractor = models.CharField(max_length=300, verbose_name='Контрагент')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма договора (руб.)')
    contract_date = models.DateField(verbose_name='Дата договора')
    status = models.CharField(
        max_length=10,
        choices=ReservationStatus.choices,
        default=ReservationStatus.ACTIVE,
        verbose_name='Статус',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Создал',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, verbose_name='Примечание')

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-contract_date']

    def __str__(self) -> str:
        return f'{self.institution.short_name} | Договор {self.contract_number} | {self.amount} руб.'
