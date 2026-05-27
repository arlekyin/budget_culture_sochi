from .models import UserRole


def get_role(user) -> str | None:
    """Возвращает роль пользователя. Суперпользователь всегда получает ADMIN."""
    if user.is_superuser:
        return UserRole.ADMIN
    try:
        return user.profile.role
    except Exception:
        return None
