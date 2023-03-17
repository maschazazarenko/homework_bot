class ApiAnswerError(Exception):
    """Выбрасывает исключение, если не удается получить ответ от сервера."""

    pass


class NoElementList(Exception):
    """Выбрасывает исключение, когда отстутствует элемент в списке ответа."""

    pass


class SendMessageError(Exception):
    """Выбрасывает исключение, когда не удается отправить сообщение ботом."""

    pass


class RequestError(Exception):
    """Выбрасывает исключение, при ошибке запроса к API."""

    pass
