"""Пользовательские сценарии: регистрация, логин, посты, лайки, комментарии."""

import pytest
from django.contrib.auth.models import User
from django.test import Client

from users.models import Comment, Like, Post


@pytest.fixture
def password() -> str:
    """Пароль для юзеров."""
    return "StrongPass!123"


@pytest.fixture
def alice(password: str) -> User:
    """Пользователь Alice + автосозданный через сигнал профиль."""
    return User.objects.create_user(username="alice", password=password)


@pytest.fixture
def bob(password: str) -> User:
    """Пользователь Bob + автосозданный через сигнал профиль."""
    return User.objects.create_user(username="bob", password=password)


@pytest.fixture
def alice_client(client: Client, alice: User) -> Client:
    """Клиент, залогиненный под Alice."""
    client.force_login(alice)
    return client


@pytest.mark.django_db
def test__registration__creates_user_and_profile(client: Client, password: str) -> None:
    """POST на /registration/ создаёт юзера и автоматически профиль (сигнал)."""
    response = client.post(
        "/registration/",
        {
            "username": "newbie",
            "password1": password,
            "password2": password,
        },
    )
    assert response.status_code == 302
    user = User.objects.get(username="newbie")
    assert user.profile is not None
    assert user.profile.avatar.name == "avatars/default_avatar.png"


@pytest.mark.django_db
def test__login__with_valid_credentials_redirects(
    client: Client, alice: User, password: str
) -> None:
    """Логин с верными данными возвращает редирект."""
    response = client.post("/login/", {"username": "alice", "password": password})
    assert response.status_code == 302


@pytest.mark.django_db
def test__login__with_wrong_password_rerenders_form(
    client: Client, alice: User
) -> None:
    """Неверный пароль не логинит и возвращает страницу логина."""
    response = client.post("/login/", {"username": "alice", "password": "wrong"})
    assert response.status_code == 200
    assert response.wsgi_request.user.is_anonymous


@pytest.mark.django_db
def test__user_profile_view__anonymous_can_view_other_user(
    client: Client, alice: User
) -> None:
    """Аноним может зайти на чужой профиль."""
    response = client.get(f"/user/{alice.id}/")
    assert response.status_code == 200
    assert b"alice" in response.content


@pytest.mark.django_db
def test__create_post__appears_on_own_wall(alice_client: Client, alice: User) -> None:
    """Создание поста добавляет запись в БД на стену автора."""
    response = alice_client.post("/post/create/", {"content": "Привет!"})
    assert response.status_code == 302
    post = Post.objects.get(author=alice)
    assert post.content == "Привет!"


@pytest.mark.django_db
def test__create_post__empty_content_is_ignored(
    alice_client: Client, alice: User
) -> None:
    """Пустой контент не создаёт пост."""
    alice_client.post("/post/create/", {"content": "   "})
    assert not Post.objects.filter(author=alice).exists()


@pytest.mark.django_db
def test__toggle_like__adds_then_removes(alice_client: Client, alice: User) -> None:
    """Повторный клик по лайку снимает его."""
    post = Post.objects.create(author=alice, content="пост")

    alice_client.post(f"/post/{post.id}/like/")
    assert Like.objects.filter(user=alice, post=post).exists()

    alice_client.post(f"/post/{post.id}/like/")
    assert not Like.objects.filter(user=alice, post=post).exists()


@pytest.mark.django_db
def test__add_comment__creates_comment(
    alice_client: Client, alice: User, bob: User
) -> None:
    """Комментарий от Alice к посту Bob создаётся."""
    post = Post.objects.create(author=bob, content="пост боба")

    alice_client.post(f"/post/{post.id}/comment/", {"content": "мой коммент"})

    comment = Comment.objects.get(post=post)
    assert comment.author == alice
    assert comment.content == "мой коммент"


@pytest.mark.django_db
def test__delete_post__forbidden_for_other_user(
    alice_client: Client, bob: User
) -> None:
    """Alice не может удалить пост Bob — 403, пост остаётся."""
    post = Post.objects.create(author=bob, content="пост боба")

    response = alice_client.post(f"/post/{post.id}/delete/")

    assert response.status_code == 403
    assert Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db
def test__delete_post__author_can_delete_own(alice_client: Client, alice: User) -> None:
    """Автор может удалить свой пост."""
    post = Post.objects.create(author=alice, content="мой пост")

    response = alice_client.post(f"/post/{post.id}/delete/")

    assert response.status_code == 302
    assert not Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db
def test__delete_comment__forbidden_for_other_user(
    alice_client: Client, alice: User, bob: User
) -> None:
    """Alice не может удалить комментарий Bob — 403, комментарий остаётся."""
    post = Post.objects.create(author=alice, content="пост")
    comment = Comment.objects.create(author=bob, post=post, content="коммент боба")

    response = alice_client.post(f"/comment/{comment.id}/delete/")

    assert response.status_code == 403
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test__delete_comment__author_can_delete_own(
    alice_client: Client, alice: User, bob: User
) -> None:
    """Автор комментария может удалить его, даже на чужой стене."""
    post = Post.objects.create(author=bob, content="пост боба")
    comment = Comment.objects.create(author=alice, post=post, content="мой коммент")

    response = alice_client.post(f"/comment/{comment.id}/delete/")

    assert response.status_code == 302
    assert not Comment.objects.filter(id=comment.id).exists()
