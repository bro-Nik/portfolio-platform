from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, NotFoundError
from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.watchlist.models import PriceAlert, WatchlistItem
from app.modules.watchlist.repositories import PriceAlertRepository, WatchlistItemRepository
from app.modules.watchlist.schemas import AlertDirection


class AlertService:
    def __init__(self, session: AsyncSession, ctx: Context, ticker_service: TickerService) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.alerts = PriceAlertRepository(session)
        self.items = WatchlistItemRepository(session)
        self.tickers = ticker_service

    async def create(
        self,
        item_id: int,
        *,
        direction: AlertDirection | None,
        target_price_usd: Decimal,
        currency_symbol: str = 'USD',
        comment: str | None = None,
    ) -> PriceAlert:
        item = await self._get_own_item(item_id)
        self._validate_target(target_price_usd)
        resolved_direction = direction or await self._derive_direction(item.ticker_id, target_price_usd)
        return await self.alerts.create(
            {
                'watchlist_item_id': item.id,
                'user_id': self.actor.id,
                'direction': resolved_direction,
                'target_price_usd': target_price_usd,
                'currency_symbol': (currency_symbol or 'USD').upper(),
                'comment': comment,
            }
        )

    async def update(
        self,
        alert_id: int,
        *,
        direction: AlertDirection | None = None,
        target_price_usd: Decimal | None = None,
        currency_symbol: str | None = None,
        comment: str | None = None,
        is_active: bool | None = None,
    ) -> PriceAlert:
        alert = await self._get_own(alert_id)
        patch: dict = {}
        if direction is not None:
            patch['direction'] = direction
        if target_price_usd is not None:
            self._validate_target(target_price_usd)
            patch['target_price_usd'] = target_price_usd
        if currency_symbol is not None:
            patch['currency_symbol'] = currency_symbol.upper()
        if comment is not None:
            patch['comment'] = comment
        if is_active is not None:
            patch['is_active'] = is_active
            if is_active:
                # Перевзведение сработавшего алерта: одноразовый становится активным заново.
                patch['triggered_at'] = None
                patch['triggered_price'] = None
        if patch:
            alert = await self.alerts.update(alert.id, patch)
        return alert

    async def archive(self, alert_id: int, archived: bool) -> PriceAlert:
        alert = await self._get_own(alert_id)
        return await self.alerts.update(alert.id, {'is_archived': archived})

    async def delete(self, alert_id: int) -> None:
        await self._get_own(alert_id)
        await self.alerts.delete(alert_id)

    async def get_triggered(self) -> list[PriceAlert]:
        alerts = await self.alerts.get_triggered_by_user(self.actor.id)
        await self._enrich(alerts)
        return alerts

    async def get_by_item(self, item_id: int) -> list[PriceAlert]:
        item = await self._get_own_item(item_id)
        return list(item.alerts)

    async def _get_own(self, alert_id: int) -> PriceAlert:
        alert = await self.alerts.get_own(alert_id, self.actor.id)
        if not alert:
            raise NotFoundError('Уведомление не найдено')
        return alert

    async def _get_own_item(self, item_id: int) -> WatchlistItem:
        item = await self.items.get_own(item_id, self.actor.id)
        if not item:
            raise NotFoundError('Запись не найдена')
        return item

    @staticmethod
    def _validate_target(target_price_usd: Decimal) -> None:
        if target_price_usd is None or target_price_usd <= 0:
            raise BusinessRuleError('Целевая цена должна быть больше нуля')

    async def _derive_direction(self, ticker_id: int, target_price_usd: Decimal) -> AlertDirection:
        """Направление из текущей цены, как в v1: порог ниже цены — ждём падение."""
        prices = await self.tickers.get_prices([ticker_id])
        current = prices.get(ticker_id)
        if current is None or current <= 0:
            raise BusinessRuleError('Нет текущей цены тикера — укажите направление явно')
        return 'below' if current >= float(target_price_usd) else 'above'

    async def _enrich(self, alerts: list[PriceAlert]) -> None:
        if not alerts:
            return
        ticker_ids = list({a.watchlist_item.ticker_id for a in alerts})
        info_map = await self.tickers.get_info(ticker_ids)
        prices = await self.tickers.get_prices(ticker_ids)
        for alert in alerts:
            self._apply_ticker_context(alert, info_map, prices)

    @staticmethod
    def _apply_ticker_context(
        alert: PriceAlert,
        info_map: dict,
        prices: dict,
    ) -> None:
        item = alert.watchlist_item
        info = info_map.get(item.ticker_id)
        if info:
            item.name = info.name
            item.symbol = info.symbol
            item.image = info.image
        item.price = prices.get(item.ticker_id)
        alert.ticker_id = item.ticker_id
        alert.ticker_symbol = getattr(item, 'symbol', None)
        alert.ticker_name = getattr(item, 'name', None)
        alert.current_price = item.price
