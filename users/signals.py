"""Сигналы приложения users."""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(
    sender: type[User], instance: User, created: bool, **kwargs: dict
) -> None:
    """Автоматически создаёт профиль при создании пользователя."""
    if created:
        Profile.objects.create(user=instance)
