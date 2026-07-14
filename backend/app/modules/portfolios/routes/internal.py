from fastapi import APIRouter
from sqlalchemy import distinct, select, union_all

from app.modules.portfolios.dependencies import DBSession
from app.modules.portfolios.models import PortfolioAsset, WalletAsset


router = APIRouter(prefix='/internal')


@router.get('/all_used_tickers')
async def get_all_used_tickers(session: DBSession) -> list:
    tickers = union_all(
        select(distinct(PortfolioAsset.ticker_id)),
        select(distinct(WalletAsset.ticker_id)),
    )
    result = await session.execute(tickers)
    return [row[0] for row in result.all() if row[0]]
