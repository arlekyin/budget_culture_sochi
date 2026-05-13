from django.db import models


class KOSGU(models.Model):
    """
    Классификатор операций сектора государственного управления.
    Определяет экономическое содержание операции.
    """

    code = models.CharField(max_length=10, unique=True, verbose_name='Код КОСГУ')
    name = models.CharField(max_length=300, verbose_name='Наименование')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'КОСГУ'
        verbose_name_plural = 'КОСГУ'
        ordering = ['code']

    def __str__(self) -> str:
        return f'{self.code} — {self.name}'


class KVR(models.Model):
    """
    Код вида расходов.
    Группирует расходы по направлениям деятельности.
    """

    code = models.CharField(max_length=10, unique=True, verbose_name='Код КВР')
    name = models.CharField(max_length=300, verbose_name='Наименование')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'КВР'
        verbose_name_plural = 'КВР'
        ordering = ['code']

    def __str__(self) -> str:
        return f'{self.code} — {self.name}'
