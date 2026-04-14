"""Вьюхи для работы с пользователями."""

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest

from users.models import Profile


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
        return render(request, "user_profile.html", {"profile_user": profile_user})
    except User.DoesNotExist:
        return render(request, "user_profile.html", {"error": "User not found"})
