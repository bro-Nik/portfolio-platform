from typing import Optional, Dict, Generator, List, Callable
from decimal import Decimal
import logging

from app.core.config import MarketTickerPrefix
from app.external_api.providers.base.client import ApiClientBase


logger = logging.getLogger(__name__)


class CoingeckoClient(ApiClientBase):
    """
    Клиент для CoinGecko API v3
    
    Документация: https://www.coingecko.com/api/documentation
    """

    BASE_URL = 'https://api.coingecko.com/api/v3'
    TIMEOUT = 30
    MAX_URL_LENGTH = 2048

    #             # Проверка статуса ответа
    #             if response.status_code == 429:
    #                 retry_after = int(response.headers.get('Retry-After', 60))
    #                 logger.warning(
    #                     f'Превышен лимит запросов к CoinGecko API. '
    #                     f'Повтор через {retry_after} секунд. '
    #                     f'Попытка {attempt + 1}/{self.MAX_RETRIES}'
    #                 )
    #                 time.sleep(retry_after)
    #                 continue
    #
    #             if response.status_code == 403 and self.API_KEY:
    #                 logger.error(
    #                     'Неверный или отсутствующий API ключ для CoinGecko. '
    #                     'Проверьте корректность ключа в настройках'
    #                 )
    #                 raise ValueError('Invalid CoinGecko API key')

    def _get_url_for_chunks_to_get_prices(self) -> str:
        return f'{self.BASE_URL}/simple/price?vs_currencies=usd&ids='

    def _calculate_safe_chunks_to_get_prices(self, ticker_ids) -> int:
        """Рассчитать количество чанков с учетом ограничения длины URL"""
        if not ticker_ids:
            return 0

        # Базовый URL для запроса цен
        url = self._get_url_for_chunks_to_get_prices()
        base_length = len(url)

        # Расчет с учетом средней длины ID
        avg_id_length = sum(len(ticker) for ticker in ticker_ids) / len(ticker_ids)
        max_ids_per_chunk = max(1, (self.MAX_URL_LENGTH - base_length) // (avg_id_length + 1))

        return int((len(ticker_ids) + max_ids_per_chunk - 1) // max_ids_per_chunk)

    def _generate_safe_chunks_to_get_prices(
        self,
        ids: List[str],
    ) -> Generator[List[str], None, None]:
        """
        Генератор, который создает безопасные чанки с учетом длины URL.
        
        Args:
            ids: Список ID тикеров
            
        Yields:
            Список ID тикеров для текущего чанка
        """
        current_chunk = []
        url = self._get_url_for_chunks_to_get_prices()
        current_length = len(url)

        for coin_id in ids:
            # Вычисляем длину добавления нового ID
            addition_length = len(coin_id) + 1  # +1 для запятой

            new_length = current_length + addition_length

            if new_length <= self.MAX_URL_LENGTH:
                current_chunk.append(coin_id)
                current_length = new_length
            else:
                # Возвращаем текущий чанк и начинаем новый
                if current_chunk:
                    yield current_chunk

                current_chunk = [coin_id]
                current_length = len(url) + 1 + len(coin_id)

        # Возвращаем последний чанк
        if current_chunk:
            yield current_chunk

    def get_prices(
        self,
        ticker_ids: List[str],
        progress_callback: Optional[Callable]  = None
    ) -> Dict[str, Decimal]:
        """
        Получить текущие цены для списка ID тикеров
        
        Args:
            ticker_ids: Список CoinGecko ID (например: ['bitcoin', 'ethereum'])
            progress_callback: Функция обратного вызова для отслеживания прогресса
        
        Returns:
            Словарь с ценами в формате {тикер: цена}
        """

        if not ticker_ids:
            return {}

        total_chunks = self._calculate_safe_chunks_to_get_prices(ticker_ids)
        failed_chunks = []
        all_results = {}

        # Обновляем прогресс если передан progress_callback
        if progress_callback:
            progress_callback(0, total_chunks, 'Начало загрузки цен CoinGecko')

        # Получаем генератор безопасных чанков
        chunks = self._generate_safe_chunks_to_get_prices(ticker_ids)

        for i, chunk in enumerate(chunks, 1):
            try:
                logger.info(f'Обработка чанка {i}/{total_chunks} ({len(chunk)} монет)')

                # Обновляем прогресс
                if progress_callback:
                    progress_callback(i, total_chunks, 'Обработка чанка загрузки цен CoinGecko')

                # Делаем запрос к API
                data = self.make_request(
                    'GET',
                    'simple/price',
                    params={
                        'vs_currencies': 'usd',
                        'ids': ','.join(chunk)
                    }
                )

                all_results.update(data)

            except Exception as e:
                logger.error(
                    f'Неожиданная ошибка при обработке чанка {i}: {e}\n'
                    f'Размер чанка: {len(chunk)} элементов\n'
                    f'Элементы чанка: {chunk[:5]}{"..." if len(chunk) > 5 else ""}'
                )
                failed_chunks.append({'chunk': i, 'ids': chunk, 'error': str(e)})
                continue

        logger.info(
            f'Пакетное оплучение цен завершено. '
            f'Получено цен: {len(all_results)}, '
            f'Ошибки: {len(failed_chunks)}, '
            f'Было запрошено: {len(ticker_ids)}'
        )

        if failed_chunks:
            logger.warning(
                f'Есть ошибки в следующих чанках: '
                f'{[fc["chunk"] for fc in failed_chunks]}'
            )

        # Формируем результат с префиксами
        price_list = {}
        for ticker_id, price_info in all_results.items():
            usd_price = price_info.get('usd')
            if usd_price is not None:
                price_list[f'{MarketTickerPrefix.CRYPTO}{ticker_id}'] = Decimal(usd_price)

        return price_list


# class CoinGeckoClient(BaseDataClient):
#     async def get_tickers(
#         self, 
#         page: int = 1, 
#         per_page: int = 100,
#         include_market_data: bool = False
#     ) -> List[CoinGeckoTicker]:
#         """
#         Получить список всех тикеров/монет
#         
#         Args:
#             page: Номер страницы
#             per_page: Количество на странице (макс 250)
#             include_market_data: Включить рыночные данные
#         
#         Returns:
#             Список объектов CoinGeckoTicker
#         """
#         try:
#             params = {
#                 "vs_currency": "usd",
#                 "order": "market_cap_desc",
#                 "per_page": min(per_page, 250),
#                 "page": page,
#                 "sparkline": "false",
#                 "locale": "en"
#             }
#             
#             if include_market_data:
#                 params.update({
#                     "price_change_percentage": "24h,7d,30d"
#                 })
#             
#             data = await self._make_request(
#                 "GET",
#                 "coins/markets",
#                 params=params
#             )
#             
#             tickers = []
#             for item in data:
#                 ticker = CoinGeckoTicker(
#                     id=item.get("id"),
#                     symbol=item.get("symbol"),
#                     name=item.get("name"),
#                     image=CoinGeckoImage(
#                         thumb=item.get("image"),
#                         small=item.get("image"),
#                         large=item.get("image")
#                     ) if item.get("image") else None,
#                     market_cap_rank=item.get("market_cap_rank"),
#                     current_price=item.get("current_price"),
#                     market_cap=item.get("market_cap"),
#                     total_volume=item.get("total_volume"),
#                     price_change_percentage_24h=item.get("price_change_percentage_24h"),
#                     last_updated=item.get("last_updated")
#                 )
#                 tickers.append(ticker)
#             
#             return tickers
#             
#         except Exception as e:
#             logger.error(f"Error fetching tickers: {e}")
#             raise
#     
#     async def get_ticker_detail(
#         self, 
#         coin_id: str,
#         include_market_data: bool = True,
#         include_community_data: bool = False,
#         include_developer_data: bool = False
#     ) -> Optional[CoinGeckoTicker]:
#         """
#         Получить детальную информацию о монете
#         
#         Args:
#             coin_id: CoinGecko ID монеты
#             include_market_data: Включить рыночные данные
#             include_community_data: Включить данные сообщества
#             include_developer_data: Включить данные разработчиков
#         
#         Returns:
#             Объект CoinGeckoTicker или None
#         """
#         try:
#             params = {
#                 "localization": "false",
#                 "tickers": "false",
#                 "market_data": str(include_market_data).lower(),
#                 "community_data": str(include_community_data).lower(),
#                 "developer_data": str(include_developer_data).lower(),
#                 "sparkline": "false"
#             }
#             
#             data = await self._make_request(
#                 "GET",
#                 f"coins/{coin_id}",
#                 params=params
#             )
#             
#             if not data:
#                 return None
#             
#             return CoinGeckoTicker(
#                 id=data.get("id"),
#                 symbol=data.get("symbol"),
#                 name=data.get("name"),
#                 platforms=data.get("platforms", {}),
#                 image=CoinGeckoImage(
#                     thumb=data.get("image", {}).get("thumb"),
#                     small=data.get("image", {}).get("small"),
#                     large=data.get("image", {}).get("large")
#                 ) if data.get("image") else None,
#                 market_data=CoinGeckoMarketData(
#                     current_price=data.get("market_data", {}).get("current_price", {}),
#                     market_cap=data.get("market_data", {}).get("market_cap", {}),
#                     total_volume=data.get("market_data", {}).get("total_volume", {}),
#                     price_change_percentage_24h=data.get("market_data", {}).get(
#                         "price_change_percentage_24h"
#                     ),
#                     market_cap_rank=data.get("market_cap_rank"),
#                     last_updated=data.get("last_updated")
#                 ) if data.get("market_data") else None,
#                 last_updated=data.get("last_updated")
#             )
#             
#         except aiohttp.ClientResponseError as e:
#             if e.status == 404:
#                 logger.warning(f"Coin {coin_id} not found")
#                 return None
#             raise
#     
#     async def get_market_chart(
#         self,
#         coin_id: str,
#         days: Union[int, str] = 1,
#         interval: str = "hourly",
#         currency: str = "usd"
#     ) -> CoinGeckoMarketChartData:
#         """
#         Получить исторические данные цен
#         
#         Args:
#             coin_id: CoinGecko ID монеты
#             days: Количество дней или 'max'
#             interval: Интервал ('daily' для days>=90, иначе 'hourly')
#             currency: Валюта
#         
#         Returns:
#             Данные рыночного графика
#         """
#         try:
#             params = {
#                 "vs_currency": currency,
#                 "days": days,
#                 "interval": interval
#             }
#             
#             data = await self._make_request(
#                 "GET",
#                 f"coins/{coin_id}/market_chart",
#                 params=params
#             )
#             
#             return CoinGeckoMarketChartData(
#                 prices=data.get("prices", []),
#                 market_caps=data.get("market_caps", []),
#                 total_volumes=data.get("total_volumes", [])
#             )
#             
#         except Exception as e:
#             logger.error(f"Error fetching market chart for {coin_id}: {e}")
#             raise
#     
#     async def get_ohlc(
#         self,
#         coin_id: str,
#         days: int = 1,
#         currency: str = "usd"
#     ) -> List[CoinGeckoOhlcData]:
#         """
#         Получить OHLC данные
#         
#         Args:
#             coin_id: CoinGecko ID монеты
#             days: Количество дней (1, 7, 14, 30, 90, 180, 365, max)
#             currency: Валюта
#         
#         Returns:
#             Список OHLC данных
#         """
#         try:
#             params = {
#                 "vs_currency": currency,
#                 "days": days
#             }
#             
#             data = await self._make_request(
#                 "GET",
#                 f"coins/{coin_id}/ohlc",
#                 params=params
#             )
#             
#             from .models import CoinGeckoOhlcData
#             
#             ohlc_list = []
#             for item in data:
#                 if len(item) >= 5:
#                     ohlc_list.append(
#                         CoinGeckoOhlcData(
#                             timestamp=datetime.fromtimestamp(item[0] / 1000),
#                             open=Decimal(str(item[1])),
#                             high=Decimal(str(item[2])),
#                             low=Decimal(str(item[3])),
#                             close=Decimal(str(item[4]))
#                         )
#                     )
#             
#             return ohlc_list
#             
#         except Exception as e:
#             logger.error(f"Error fetching OHLC for {coin_id}: {e}")
#             raise
#     
#     async def search_tickers(
#         self, 
#         query: str, 
#         limit: int = 10
#     ) -> List[CoinGeckoTicker]:
#         """
#         Поиск монет по названию или символу
#         
#         Args:
#             query: Поисковый запрос
#             limit: Максимальное количество результатов
#         
#         Returns:
#             Список найденных тикеров
#         """
#         try:
#             data = await self._make_request(
#                 "GET",
#                 "search",
#                 params={"query": query}
#             )
#             
#             tickers = []
#             for coin in data.get("coins", [])[:limit]:
#                 ticker = CoinGeckoTicker(
#                     id=coin.get("id"),
#                     symbol=coin.get("symbol"),
#                     name=coin.get("name"),
#                     market_cap_rank=coin.get("market_cap_rank")
#                 )
#                 tickers.append(ticker)
#             
#             return tickers
#             
#         except Exception as e:
#             logger.error(f"Error searching tickers: {e}")
#             raise
#     
#     async def get_api_status(self) -> CoinGeckoResponseStatus:
#         """Получить статус API и использование"""
#         try:
#             data = await self._make_request("GET", "ping")
#             
#             # Для Pro API
#             if self.api_key:
#                 # Получаем данные об использовании из заголовков
#                 return CoinGeckoResponseStatus(
#                     total_requests=1000000,  # Пример для Pro
#                     total_request_cap=1000000,
#                     remaining_requests=999000,
#                     requests_used=1000,
#                     reset_time=datetime.utcnow() + timedelta(days=30)
#                 )
#             
#             return CoinGeckoResponseStatus(
#                 total_requests=10000,  # Бесплатный лимит
#                 total_request_cap=10000,
#                 remaining_requests=9500,
#                 requests_used=500,
#                 reset_time=datetime.utcnow() + timedelta(days=30)
#             )
#             
#         except Exception as e:
#             logger.error(f"Error getting API status: {e}")
#             raise
#     
#     async def _find_coin_id_by_symbol(self, symbol: str) -> Optional[str]:
#         """Найти coin_id по символу"""
#         try:
#             search_results = await self.search_tickers(symbol, limit=5)
#             for ticker in search_results:
#                 if ticker.symbol.lower() == symbol.lower():
#                     return ticker.id
#             return None
#         except Exception:
#             return None
#     
#     async def close(self):
#         """Закрыть сессию"""
#         if self.session:
#             await self.session.close()
#     
#     def __del__(self):
#         """Деструктор"""
#         if hasattr(self, 'session') and self.session:
#             asyncio.create_task(self.close())
