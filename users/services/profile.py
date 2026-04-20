"""Операции над профилем пользователя."""

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile


def change_username(user: User, new_username: str | None) -> str | None:
    """Меняет username. Возвращает текст ошибки или None при успехе."""
    new_username = (new_username or "").strip()
    if not new_username:
        return "Имя пользователя не может быть пустым"
    if User.objects.filter(username=new_username).exclude(id=user.id).exists():
        return "Пользователь с таким именем уже существует"
    user.username = new_username
    user.save()
    return None


def change_avatar(user: User, avatar: UploadedFile) -> None:
    """Заменяет аватар пользователя."""
    profile = user.profile
    profile.avatar = avatar
    profile.save()
