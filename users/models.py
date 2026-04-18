"""Различные модели."""

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Модель для привязки аватара к пользователю."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default_avatar.png"
    )


class Post(models.Model):
    """Пост на стене пользователя."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wall_posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки модели Post."""

        ordering = ["-created_at"]


class Like(models.Model):
    """Лайк на пост."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки модели Like."""

        unique_together = ("user", "post")


class Comment(models.Model):
    """Комментарий к посту."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки модели Comment."""

        ordering = ["created_at"]
