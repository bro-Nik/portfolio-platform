from itertools import product


def combine_ids_and_tickers(
    ids: list[int | None],
    tickers: list[str | None],
) -> list[tuple[int, str]]:
    clean_ids = [i for i in ids if i]
    clean_tickers = [t for t in tickers if t]
    return list({(i, t) for i, t in product(clean_ids, clean_tickers)})
