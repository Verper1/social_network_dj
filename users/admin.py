"""Регистрация моделей в админке."""

from django.contrib import admin

from users.models import Profile, Post, Like, Comment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "birth_date", "status")
    search_fields = ("user__username", "user__email", "city", "status")
    list_filter = ("city", "birth_date")
    raw_id_fields = ("user",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created_at")
    search_fields = ("author__username", "content")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("author",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username", "post__content")
    list_filter = ("created_at",)
    raw_id_fields = ("user", "post")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at")
    search_fields = ("author__username", "content")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("author", "post")
