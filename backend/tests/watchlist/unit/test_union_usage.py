from app.di import UnionTickerUsageRepository


class _Reader:
    def __init__(self, ids: list[int], counts: dict[int, int]) -> None:
        self._ids = ids
        self._counts = counts
        self.reassigned: list[tuple[int, int]] = []

    async def get_used_ticker_ids(self, market: str | None = None) -> list[int]:
        return self._ids

    async def count_references(self, ticker_id: int) -> int:
        return self._counts.get(ticker_id, 0)

    async def reassign_references(self, source_id: int, target_id: int) -> None:
        self.reassigned.append((source_id, target_id))


class TestUnionTickerUsageRepository:
    async def test_get_used_ticker_ids_unions_and_dedupes(self):
        union = UnionTickerUsageRepository(_Reader([1, 2], {}), _Reader([2, 3], {}))

        assert await union.get_used_ticker_ids() == [1, 2, 3]
        assert await union.get_used_ticker_ids('crypto') == [1, 2, 3]

    async def test_count_references_sums(self):
        union = UnionTickerUsageRepository(_Reader([], {1: 3}), _Reader([], {1: 2, 2: 1}))

        assert await union.count_references(1) == 5
        assert await union.count_references(2) == 1
        assert await union.count_references(999) == 0

    async def test_reassign_references_delegates_to_both(self):
        portfolios, watchlist = _Reader([], {}), _Reader([], {})
        union = UnionTickerUsageRepository(portfolios, watchlist)

        await union.reassign_references(1, 2)

        assert portfolios.reassigned == [(1, 2)]
        assert watchlist.reassigned == [(1, 2)]
