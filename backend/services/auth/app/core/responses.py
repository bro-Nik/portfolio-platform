"""Общие ответы API для обработки ошибок."""

from app.schemas import ErrorResponse

RESPONSES = {
    400: {'model': ErrorResponse},
    401: {'model': ErrorResponse},
    403: {'model': ErrorResponse},
    404: {'model': ErrorResponse},
    409: {'model': ErrorResponse},
    422: {'model': ErrorResponse},
    500: {'model': ErrorResponse},
}


def get_responses(*codes: int) -> dict:
    """Формирует responses на основе кодов ответов."""
    skip = {200}
    return {code: RESPONSES[code] for code in codes if code not in skip}


POST_RESPONSES = get_responses(400, 401, 403, 404, 409, 500)
GET_RESPONSES = get_responses(400, 401, 403, 404, 500)
PUT_RESPONSES = get_responses(400, 401, 403, 404, 409, 500)
DELETE_RESPONSES = get_responses(400, 401, 403, 404, 500)
