from app.core.celery import celery
from app.external_api.management.manager import ApiManager


@celery.task(bind=True)
def update_market_data(self, api_provider = None, method = None, **kwargs):
    """Универсальная задача для работы с внешними API"""
    if not (api_provider and method):
        return {'status': 'error', 'message': 'Отсутствуют переменные api_provider или method'}

    api_manager = ApiManager(api_provider)
    result = api_manager.execute(method, **kwargs)

    return result
