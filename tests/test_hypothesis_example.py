from hypothesis import given
from hypothesis import strategies as st

from users.models import Post


@given(content=st.text())
def test__post_content_roundtrip(content: str) -> None:
    """Модель Post сохраняет контент без изменений для любой строки."""
    post = Post(content=content)
    assert post.content == content
