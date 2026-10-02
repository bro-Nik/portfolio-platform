from datetime import UTC, datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.watchlist.models import PriceAlert
from app.modules.watchlist.protocols import UserEmailReader
from app.modules.watchlist.repositories import PriceAlertRepository
from app.modules.watchlist.tasks.price_alert import send_price_alert_email

logger = logging.getLogger(__name__)


class AlertEvaluatorService:
    """Реализация market.protocols.PriceUpdateObserver.

    Вызывается из TickerService.save_prices после коммита новых цен.
    Одноразовая семантика: сработавший алерт сразу деактивируется, повторный
    прогон по тем же ценам ничего не делает — письмо не дублируется.
    """

    def __init__(self, session: AsyncSession, users: UserEmailReader) -> None:
        self._session = session
        self._alerts = PriceAlertRepository(session)
        self._users = users

    async def on_prices_updated(self, prices: dict[int, float]) -> None:
        if not prices:
            return
        active = await self._alerts.get_active_by_ticker_ids(list(prices))
        if not active:
            return

        now = datetime.now(UTC)
        fired = [alert for alert in active if self._is_hit(alert, prices)]
        if not fired:
            return

        emails = await self._users.get_emails(list({a.user_id for a in fired}))
        for alert in fired:
            alert.triggered_at = now
            alert.triggered_price = prices[alert.watchlist_item.ticker_id]
            alert.is_active = False
        await self._session.commit()

        for alert in fired:
            email = emails.get(alert.user_id)
            if not email:
                logger.warning(
                    'Алерт %s сработал, но email пользователя %s недоступен — письмо пропущено',
                    alert.id,
                    alert.user_id,
                )
                continue
            await send_price_alert_email.kiq(alert_id=alert.id, email=email)

    @staticmethod
    def _is_hit(alert: PriceAlert, prices: dict[int, float]) -> bool:
        price = prices.get(alert.watchlist_item.ticker_id)
        if price is None or price <= 0:
            return False
        target = float(alert.target_price_usd)
        if alert.direction == 'above':
            return price >= target
        if alert.direction == 'below':
            return price <= target
        return False
