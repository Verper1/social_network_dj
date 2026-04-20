"""Вьюхи для работы с пользователями."""

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest

from users.forms import ProfileInfoForm
from users.models import Post, Comment
from users.services import comments, feed, posts, profile


def registration_view(request: HttpRequest) -> HttpResponse:
    """Регистрация пользователя."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration.html", {"form": form})


def _profile_context(request: HttpRequest, **overrides: object) -> dict[str, object]:
    """Базовый контекст для страницы настроек профиля."""
    context: dict[str, object] = {
        "password_form": PasswordChangeForm(request.user),
        "profile_form": ProfileInfoForm(instance=request.user.profile),
    }
    context.update(overrides)
    return context


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Просмотр профиля пользователя."""
    return render(request, "profile.html", _profile_context(request))


@login_required
def change_avatar(request: HttpRequest) -> HttpResponse:
    """Изменение аватара пользователя."""
    if request.method == "POST" and request.FILES.get("avatar"):
        profile.change_avatar(request.user, request.FILES["avatar"])
        return redirect("profile")

    return render(request, "profile.html", _profile_context(request))


@login_required
def change_username(request: HttpRequest) -> HttpResponse:
    """Изменение имени пользователя."""
    error_message = None

    if request.method == "POST":
        error_message = profile.change_username(
            request.user, request.POST.get("username")
        )
        if error_message is None:
            return redirect("profile")

    return render(
        request,
        "profile.html",
        _profile_context(request, username_error=error_message),
    )


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    """Изменение пароля пользователя."""
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("profile")

    return render(
        request, "profile.html", _profile_context(request, password_form=form)
    )


@login_required
def change_profile_info(request: HttpRequest) -> HttpResponse:
    """Сохранение персональной информации (bio, дата рождения, город, статус)."""
    user_profile = request.user.profile

    if request.method == "POST":
        form = ProfileInfoForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileInfoForm(instance=user_profile)

    return render(request, "profile.html", _profile_context(request, profile_form=form))


def all_profiles_view(request: HttpRequest) -> HttpResponse:
    """Главная страница и просмотр всех профилей."""
    users = User.objects.all()
    return render(request, "all_profiles.html", {"users": users})


def user_profile_view(request: HttpRequest, user_id: int) -> HttpResponse:
    """Просмотр профиля пользователя."""
    profile_user = get_object_or_404(User, id=user_id)
    posts_data = feed.build_wall_feed(request.user, profile_user)
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
@require_POST
def create_post(request: HttpRequest) -> HttpResponse:
    """Создание поста на своей стене."""
    posts.create_post(request.user, request.POST.get("content", ""))
    return redirect("user_profile", user_id=request.user.id)


@login_required
@require_POST
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """Удаление собственного поста."""
    post = get_object_or_404(Post, id=post_id)
    author_id = post.author_id
    posts.delete_post(request.user, post)
    return redirect("user_profile", user_id=author_id)


@login_required
@require_POST
def toggle_like(request: HttpRequest, post_id: int) -> HttpResponse:
    """Поставить/убрать лайк посту."""
    post = get_object_or_404(Post, id=post_id)
    posts.toggle_like(request.user, post)
    return redirect("user_profile", user_id=post.author_id)


@login_required
@require_POST
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    comments.add_comment(request.user, post, request.POST.get("content", ""))
    return redirect("user_profile", user_id=post.author_id)


@login_required
@require_POST
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    """Удаление собственного комментария."""
    comment = get_object_or_404(Comment, id=comment_id)
    wall_owner_id = comment.post.author_id
    comments.delete_comment(request.user, comment)
    return redirect("user_profile", user_id=wall_owner_id)
