"""URL configuration for social_media1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from users.views import (
    registration_view,
    profile_view,
    all_profiles_view,
    change_username,
    change_password,
    change_avatar,
    change_profile_info,
    user_profile_view,
    create_post,
    delete_post,
    toggle_like,
    add_comment,
    delete_comment,
)
from social_media_settings import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registration/", registration_view, name="registration"),
    path("profile/", profile_view, name="profile"),
    path("profile/username/", change_username, name="change_username"),
    path("profile/password/", change_password, name="change_password"),
    path("profile/avatar/", change_avatar, name="change_avatar"),
    path("profile/info/", change_profile_info, name="change_profile_info"),
    path("user/<int:user_id>/", user_profile_view, name="user_profile"),
    path("post/create/", create_post, name="create_post"),
    path("post/<int:post_id>/delete/", delete_post, name="delete_post"),
    path("post/<int:post_id>/like/", toggle_like, name="toggle_like"),
    path("post/<int:post_id>/comment/", add_comment, name="add_comment"),
    path("comment/<int:comment_id>/delete/", delete_comment, name="delete_comment"),
    path("", all_profiles_view, name="all_profiles"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
