import logging
from pathlib import Path

from dishka.integrations.taskiq import inject

from app.common.email import Mailer
from app.core import settings
from app.core.taskiq import broker
from app.modules.market.dependencies.di import TickerCatalogDep
from app.modules.watchlist.dependencies.deps import SessionDep
from app.modules.watchlist.repositories import PriceAlertRepository

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'email'

_mailer = Mailer(TEMPLATE_DIR)

_DIRECTION_WORDS = {
    'above': ('выше', 'вырос выше'),
    'below': ('ниже', 'упал ниже'),
}


def _format_amount(value: float) -> str:
    if value >= 1000:
        return f'{value:,.0f}'.replace(',', ' ')
    if value >= 1:
        return f'{value:,.2f}'.replace(',', ' ')
    return f'{value:.8f}'.rstrip('0').rstrip('.')


@broker.task(task_name='send_price_alert_email')
@inject(patch_module=True)
async def send_price_alert_email(
    session: SessionDep,
    tickers: TickerCatalogDep,
    alert_id: int,
    email: str,
) -> None:
    """Отправить письмо о сработавшем ценовом алерте.

    Алерт уже помечен сработавшим в той же транзакции, что и проверка цен:
    задача только собирает контекст и отправляет письмо.
    """
    alert = await PriceAlertRepository(session).get(alert_id, relations=('watchlist_item',))
    if not alert or alert.triggered_at is None:
        logger.info('Алерт %s не найден или не сработал — письмо пропущено', alert_id)
        return

    item = alert.watchlist_item
    info_map = await tickers.get_info([item.ticker_id])
    info = info_map.get(item.ticker_id)
    symbol = info.symbol if info and info.symbol else f'#{item.ticker_id}'
    name = info.name if info and info.name else symbol

    rate = await tickers.get_price_by_symbol('currency', alert.currency_symbol)
    currency = alert.currency_symbol if rate else 'USD'
    divisor = rate or 1.0

    def _display(value: float) -> str:
        return f'{_format_amount(value / divisor)} {currency}'

    target_display = _display(float(alert.target_price_usd))
    triggered_display = _display(float(alert.triggered_price)) if alert.triggered_price else '—'

    word, verb = _DIRECTION_WORDS.get(alert.direction, ('', ''))
    await _mailer.send(
        email,
        f'{symbol}: цена {word} {target_display}',
        'price_alert',
        {
            'email': email,
            'ticker_name': name,
            'ticker_symbol': symbol,
            'direction_word': word,
            'direction_verb': verb,
            'target_display': target_display,
            'triggered_display': triggered_display,
            'comment': alert.comment,
            'frontend_url': settings.frontend_url,
        },
        what=f'письмо о срабатывании алерта {alert_id}',
    )
