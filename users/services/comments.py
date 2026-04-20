"""Операции над комментариями."""

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from users.models import Comment, Post


def add_comment(author: User, post: Post, content: str) -> Comment | None:
    """Добавляет комментарий. Пустой/пробельный контент игнорируется."""
    content = content.strip()
    if not content:
        return None
    return Comment.objects.create(author=author, post=post, content=content)


def delete_comment(actor: User, comment: Comment) -> None:
    """Удаляет комментарий. Только автор имеет право."""
    if comment.author_id != actor.id:
        raise PermissionDenied("Нельзя удалить чужой комментарий")
    comment.delete()
