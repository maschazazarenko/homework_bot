class InvalidTockenError(Exception):
    """Выбрасывает исключения, если отсутствуют переменные."""

    pass


class ApiAnswerError(Exception):
    """Выбрасывает исключение, если не удается получить ответ от сервера."""

    pass


class NoElementList(Exception):
    """Выбрасывает исключение, когда отстутствует элемент в списке ответа."""

    pass
