"""Формы приложения users."""

from django import forms

from users.models import Profile


class ProfileInfoForm(forms.ModelForm):
    """Форма редактирования персональной информации профиля."""

    class Meta:
        """Настройки профиля."""

        model = Profile
        fields = ("bio", "birth_date", "city", "status")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "city": forms.TextInput(),
            "status": forms.TextInput(),
        }
        labels = {
            "bio": "О себе",
            "birth_date": "Дата рождения",
            "city": "Город",
            "status": "Статус",
        }
