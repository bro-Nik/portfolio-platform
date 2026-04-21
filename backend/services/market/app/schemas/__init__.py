from pydantic import BaseModel

from .provider import (
    ProviderCreate,
    ProviderCreateRequest,
    ProviderLog,
    ProviderResponse,
    ProviderStats,
    ProviderUpdate,
    ProviderUpdateRequest,
)
from .request_log import RequestLogCreate, RequestLogUpdate
from .task import (
    TaskCreate,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdate,
    TaskUpdateRequest,
)
from .ticker import ImagesResponse, PricesResponse, TickerInfoListResponse, TickerSearchResponse

TaskResponse.model_rebuild()
