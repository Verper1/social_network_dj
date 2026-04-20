"""Различные модели."""

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Профиль пользователя."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default_avatar.png"
    )
    bio = models.TextField(blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return f"Профиль {self.user.username}"


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

    def __str__(self) -> str:
        preview = self.content[:30]
        return f"{self.author.username}: {preview}"


class Like(models.Model):
    """Лайк на пост."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки модели Like."""

        unique_together = ("user", "post")

    def __str__(self) -> str:
        return f"{self.user.username} ♥ пост #{self.post_id}"


class Comment(models.Model):
    """Комментарий к посту."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Настройки модели Comment."""

        ordering = ["created_at"]

    def __str__(self) -> str:
        preview = self.content[:30]
        return f"{self.author.username} → пост #{self.post_id}: {preview}"
