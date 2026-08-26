"""Общие хелперы обогащения read-моделей портфелей и кошельков."""

from collections.abc import Awaitable, Callable
from typing import Any

from app.modules.market.services.ticker import TickerService


async def enrich_assets_with_ticker_info(assets: list[Any], ticker_service: TickerService) -> None:
    """Проставляет активам имя/символ/картинку/рынок из market-кеша."""
    if not assets:
        return
    ticker_ids = list({a.ticker_id for a in assets})
    info_map = await ticker_service.get_info(ticker_ids)
    for asset in assets:
        info = info_map.get(asset.ticker_id)
        if info:
            asset.name = info.name
            asset.symbol = info.symbol
            asset.image = info.image
            asset.market = info.market


def group_assets_by_parent(parents: list[Any]) -> tuple[dict[int, list[Any]], dict[int, int]]:
    """Группирует активы по родителю: ({parent_id: [assets]}, {asset_id: parent_id})."""
    assets_by_parent: dict[int, list[Any]] = {}
    parent_per_asset: dict[int, int] = {}
    for parent in parents:
        assets_by_parent[parent.id] = []
        for asset in parent.assets:
            assets_by_parent[parent.id].append(asset)
            parent_per_asset[asset.id] = parent.id
    return assets_by_parent, parent_per_asset


async def add_has_transactions(
    parents: list[Any],
    all_assets: list[Any],
    *,
    parents_with_transactions: Callable[[list[int]], Awaitable[set[int]]],
    parent_tickers_with_transactions: Callable[[dict[int, list[int]]], Awaitable[set[tuple[int, int]]]],
) -> None:
    """Проставляет флаги has_transactions родителям и активам.

    `parents_with_transactions(ids)` и `parent_tickers_with_transactions(mapping)`
    — колбэки над репозиторием транзакций (портфельные или кошельковые варианты).
    """
    parent_ids = [p.id for p in parents]
    txn_parent_ids = await parents_with_transactions(parent_ids)
    for parent in parents:
        parent.has_transactions = parent.id in txn_parent_ids

    assets_by_parent, parent_per_asset = group_assets_by_parent(parents)
    parent_tickers = {pid: [a.ticker_id for a in assets] for pid, assets in assets_by_parent.items()}
    txn_pairs = await parent_tickers_with_transactions(parent_tickers)
    for asset in all_assets:
        asset.has_transactions = (parent_per_asset[asset.id], asset.ticker_id) in txn_pairs
