import deal


@deal.pre(lambda content: isinstance(content, str))
@deal.ensure(lambda content, result: result == (content.strip() == ""))
def is_empty_post(content: str) -> bool:
    """Проверить, что контент поста пустой после удаления пробелов."""
    return content.strip() == ""


test__is_empty_post_contracts = deal.cases(is_empty_post)
