from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile, UserRole


class Command(BaseCommand):
    help = 'Создаёт UserProfile для пользователей, у которых его нет. Суперпользователям назначает роль admin.'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        updated_count = 0

        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                if user.is_superuser:
                    profile.role = UserRole.ADMIN
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'  [{user.username}] создан профиль с ролью ADMIN (суперпользователь)')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  [{user.username}] создан профиль с ролью DIRECTOR (по умолчанию)')
                    )
                created_count += 1
            else:
                # Если профиль был, но суперпользователь — убеждаемся что роль admin
                if user.is_superuser and profile.role != UserRole.ADMIN:
                    profile.role = UserRole.ADMIN
                    profile.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  [{user.username}] роль обновлена до ADMIN (суперпользователь)')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nГотово: создано профилей={created_count}, обновлено={updated_count}'
            )
        )
