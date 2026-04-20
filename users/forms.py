"""Формы приложения users."""

import json
from datetime import date
from functools import lru_cache
from pathlib import Path

from django import forms

from users.models import Profile

MIN_AGE = 14
_CITIES_JSON = Path(__file__).parent / "data" / "russian_cities.json"


@lru_cache(maxsize=1)
def _russian_cities() -> list[tuple[str, str]]:
    """Загружает список городов из JSON-файла."""
    names: list[str] = json.loads(_CITIES_JSON.read_text(encoding="utf-8"))
    return [("", "Не указан"), *((name, name) for name in names)]


class ProfileInfoForm(forms.ModelForm):
    """Форма редактирования персональной информации профиля."""

    city = forms.ChoiceField(choices=[], required=False, label="Город")

    class Meta:
        """Настройки профиля."""

        model = Profile
        fields = ("bio", "birth_date", "city", "status")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "bio": "О себе",
            "birth_date": "Дата рождения",
            "status": "Статус",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Подставляет список городов при инстансе."""
        super().__init__(*args, **kwargs)
        self.fields["city"].choices = _russian_cities()

    def clean_birth_date(self) -> date | None:
        """Разрешает только даты, соответствующие возрасту ≥ MIN_AGE лет."""
        birth_date: date | None = self.cleaned_data.get("birth_date")
        if birth_date is None:
            return None

        today = date.today()
        if birth_date > today:
            raise forms.ValidationError("Дата рождения не может быть в будущем.")

        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        if age < MIN_AGE:
            raise forms.ValidationError(
                f"Пользователь должен быть не младше {MIN_AGE} лет."
            )
        return birth_date
