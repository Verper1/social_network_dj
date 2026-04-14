import pytest
from django.test import Client


@pytest.mark.django_db
def test__all_profiles_view__show_main_page(client: Client) -> None:
    """Проверка, что главная страница отображается."""
    response = client.get("/")
    assert response.status_code == 200
