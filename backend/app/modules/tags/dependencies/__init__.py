from dishka import FromDishka

from .di import TagsProvider
from app.common.dependencies import require_user
from app.modules.tags.services.tag import TagService

TagServiceDep = FromDishka[TagService]

__all__ = [
    'TagServiceDep',
    'TagsProvider',
    'require_user',
]
