class EndpointNotAvailable(Exception):
    """Доступность параметров запроса."""

    pass


class HTTPStatusError(Exception):
    """Статус ответа."""

    pass
