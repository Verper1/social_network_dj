"""Вьюхи для работы с пользователями."""

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseForbidden

from users.models import Profile, Post, Like, Comment


def registration_view(request: HttpRequest) -> HttpResponse:
    """Регистрация пользователя."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration.html", {"form": form})


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Просмотр профиля пользователя."""
    password_form = PasswordChangeForm(request.user)
    return render(request, "profile.html", {"password_form": password_form})


@login_required
def change_avatar(request: HttpRequest) -> HttpResponse:
    """Изменение аватара пользователя."""
    if request.method == "POST" and request.FILES.get("avatar"):
        profile = request.user.profile
        profile.avatar = request.FILES["avatar"]
        profile.save()
        return redirect("profile")

    password_form = PasswordChangeForm(request.user)
    return render(request, "profile.html", {"password_form": password_form})


@login_required
def change_username(request: HttpRequest) -> HttpResponse:
    """Изменение имени пользователя."""
    error_message = None

    if request.method == "POST":
        new_username = request.POST.get("username")

        if not new_username:
            error_message = "Имя пользователя не может быть пустым"
        elif User.objects.filter(username=new_username).exists():
            error_message = "Пользователь с таким именем уже существует"
        else:
            request.user.username = new_username
            request.user.save()
            return redirect("profile")

    password_form = PasswordChangeForm(request.user)
    return render(
        request,
        "profile.html",
        {"password_form": password_form, "username_error": error_message},
    )


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    """Изменение пароля пользователя."""
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("profile")

    return render(request, "profile.html", {"password_form": form})


def all_profiles_view(request: HttpRequest) -> HttpResponse:
    """Главная страница и просмотр всех профилей."""
    users = User.objects.all()
    return render(request, "all_profiles.html", {"users": users})


def user_profile_view(request: HttpRequest, user_id: int) -> HttpResponse:
    """Просмотр профиля пользователя."""
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, "user_profile.html", {"error": "User not found"})

    posts = (
        Post.objects.filter(author=profile_user)
        .select_related("author")
        .prefetch_related("likes", "comments__author")
    )

    liked_post_ids: set[int] = set()
    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(user=request.user, post__in=posts).values_list(
                "post_id", flat=True
            )
        )

    posts_data = [
        {
            "post": post,
            "likes_count": post.likes.count(),
            "is_liked": post.id in liked_post_ids,
            "comments": post.comments.all(),
        }
        for post in posts
    ]

    is_own_wall = request.user.is_authenticated and request.user.id == profile_user.id

    return render(
        request,
        "user_profile.html",
        {
            "profile_user": profile_user,
            "posts_data": posts_data,
            "is_own_wall": is_own_wall,
        },
    )


@login_required
def create_post(request: HttpRequest) -> HttpResponse:
    """Создание поста на своей стене."""
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(author=request.user, content=content)

    return redirect("user_profile", user_id=request.user.id)


@login_required
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """Удаление собственного поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author_id != request.user.id:
        return HttpResponseForbidden("Нельзя удалить чужой пост")

    author_id = post.author_id
    if request.method == "POST":
        post.delete()

    return redirect("user_profile", user_id=author_id)


@login_required
def toggle_like(request: HttpRequest, post_id: int) -> HttpResponse:
    """Поставить/убрать лайк посту."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()

    return redirect("user_profile", user_id=post.author_id)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(author=request.user, post=post, content=content)

    return redirect("user_profile", user_id=post.author_id)


@login_required
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    """Удаление собственного комментария."""
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author_id != request.user.id:
        return HttpResponseForbidden("Нельзя удалить чужой комментарий")

    wall_owner_id = comment.post.author_id
    if request.method == "POST":
        comment.delete()

    return redirect("user_profile", user_id=wall_owner_id)
