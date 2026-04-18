from datetime import datetime, timezone

import pytest
from django.contrib.auth.models import User
from freezegun import freeze_time

from users.models import Post, Profile


@pytest.mark.django_db
def test__post_created_at_matches_frozen_time() -> None:
    """Пост, созданный под freeze_time, имеет замороженную дату."""
    user = User.objects.create_user(username="alice", password="StrongPass!123")
    Profile.objects.create(user=user)

    with freeze_time("2026-01-15 12:30:00"):
        post = Post.objects.create(author=user, content="Привет, стена!")

    assert post.created_at == datetime(2026, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
