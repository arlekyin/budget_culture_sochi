from django.db import models


class InstitutionType(models.TextChoices):
    LIBRARY = 'library', 'Библиотека'
    MUSEUM = 'museum', 'Музей'
    THEATER = 'theater', 'Театр'
    CULTURE_HOUSE = 'culture_house', 'Дом культуры'
    ART_SCHOOL = 'art_school', 'Школа искусств / ДМШ'
    OTHER = 'other', 'Иное'


class Institution(models.Model):
    """Учреждение культуры г. Сочи."""

    name = models.CharField(max_length=300, verbose_name='Полное наименование')
    short_name = models.CharField(max_length=100, verbose_name='Краткое наименование')
    institution_type = models.CharField(
        max_length=20,
        choices=InstitutionType.choices,
        default=InstitutionType.OTHER,
        verbose_name='Тип учреждения',
    )
    inn = models.CharField(max_length=12, blank=True, verbose_name='ИНН')
    address = models.CharField(max_length=300, blank=True, verbose_name='Адрес')
    head_name = models.CharField(max_length=200, blank=True, verbose_name='ФИО руководителя')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Учреждение'
        verbose_name_plural = 'Учреждения'
        ordering = ['short_name']

    def __str__(self) -> str:
        return self.short_name


class BudgetLimit(models.Model):
    """Лимит финансирования для учреждения на год."""

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='limits',
        verbose_name='Учреждение',
    )
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    total_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Общий лимит (руб.)',
    )
    set_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Установил',
    )
    set_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, verbose_name='Примечание')

    class Meta:
        verbose_name = 'Лимит финансирования'
        verbose_name_plural = 'Лимиты финансирования'
        unique_together = ('institution', 'year')

    def __str__(self) -> str:
        return f'{self.institution.short_name} — {self.year}: {self.total_limit} руб.'
