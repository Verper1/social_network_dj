"""Операции над постами и лайками."""

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from users.models import Like, Post


def create_post(author: User, content: str) -> Post | None:
    """Создаёт пост. Пустой/пробельный контент игнорируется."""
    content = content.strip()
    if not content:
        return None
    return Post.objects.create(author=author, content=content)


def delete_post(actor: User, post: Post) -> None:
    """Удаляет пост. Только автор имеет право."""
    if post.author_id != actor.id:
        raise PermissionDenied("Нельзя удалить чужой пост")
    post.delete()


def toggle_like(user: User, post: Post) -> bool:
    """Ставит или снимает лайк. Возвращает True, если поставлен."""
    like, created = Like.objects.get_or_create(user=user, post=post)
    if not created:
        like.delete()
    return created
