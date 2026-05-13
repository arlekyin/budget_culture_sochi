from django.db import models
from django.contrib.auth.models import User


class UserRole(models.TextChoices):
    """Роли пользователей в системе."""
    DIRECTOR = 'director', 'Директор учреждения'
    ACCOUNTANT = 'accountant', 'Бухгалтер ЦБ'
    ADMIN = 'admin', 'Администратор системы'
    HEAD = 'head', 'Руководитель Управления культуры'


class UserProfile(models.Model):
    """Профиль пользователя с ролью и привязкой к учреждению."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.DIRECTOR,
        verbose_name='Роль',
    )
    # Заполняется только для роли DIRECTOR
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Учреждение',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self) -> str:
        return f'{self.user.get_full_name() or self.user.username} ({self.get_role_display()})'

    @property
    def is_director(self) -> bool:
        return self.role == UserRole.DIRECTOR

    @property
    def is_accountant(self) -> bool:
        return self.role == UserRole.ACCOUNTANT

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_head(self) -> bool:
        return self.role == UserRole.HEAD
