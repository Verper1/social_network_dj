"""Сборка ленты постов для отображения."""

from django.contrib.auth.models import AnonymousUser, User

from users.models import Like, Post


def build_wall_feed(
    viewer: User | AnonymousUser, profile_user: User
) -> list[dict[str, object]]:
    """Собирает данные о постах со стены для шаблона."""
    posts = (
        Post.objects.filter(author=profile_user)
        .select_related("author")
        .prefetch_related("likes", "comments__author")
    )

    liked_post_ids: set[int] = set()
    if viewer.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(user=viewer, post__in=posts).values_list(
                "post_id", flat=True
            )
        )

    return [
        {
            "post": post,
            "likes_count": post.likes.count(),
            "is_liked": post.id in liked_post_ids,
            "comments": post.comments.all(),
        }
        for post in posts
    ]
