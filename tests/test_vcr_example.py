import urllib.request

import vcr

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    record_mode="once",
)


def fetch_github_bio(username: str) -> int:
    """Получить HTTP-статус ответа GitHub API о пользователе."""
    url = f"https://api.github.com/users/{username}"
    with urllib.request.urlopen(url) as response:
        return response.status


@my_vcr.use_cassette("github_octocat.yaml")
def test__github_bio_status() -> None:
    """Запрос к GitHub играется из кассеты и возвращает 200."""
    assert fetch_github_bio("octocat") == 200
