import type { QueryClient } from '@tanstack/react-query';

/**
 * Ключи запросов и инвалидация.
 *
 * Раньше каждый модуль держал свой набор ключей строкой и половина мутаций
 * не инвалидировала ничего: оптимистичные правки оставались в кэше, пока
 * кто-то вручную не нажмёт «Обновить».
 */

export const queryKeys = {
  overview: ['overview'],
  tags: ['tags'],
  portfolioAssetTransactions: ['portfolioAssetTransactions'],
  walletAssetTransactions: ['walletAssetTransactions'],
  assetPrices: ['assetPrices'],
  currencies: ['currencies'],
  profile: ['profile'],
  sessions: ['sessions'],
  watchlist: ['watchlist'],
  triggeredAlerts: ['triggeredAlerts'],
};

/** Ключи, которые зависят от данных портфелей, кошельков, активов и транзакций. */
export const portfolioDataKeys = [
  queryKeys.overview,
  queryKeys.portfolioAssetTransactions,
  queryKeys.walletAssetTransactions,
  queryKeys.assetPrices,
];

export const invalidateKeys = (queryClient: QueryClient, keys: readonly (readonly string[])[]): Promise<void[]> =>
  Promise.all(keys.map((queryKey) => queryClient.invalidateQueries({ queryKey: [...queryKey] })));

/**
 * Синхронизировать кэш с сервером после мутации.
 *
 * Вызывается в onSettled: оптимистичное обновление в onMutate отвечает за
 * отзывчивость, а этот вызов — за то, что кэш сходится с реальными данными
 * даже если сервер посчитал что-то иначе.
 */
export const reconcilePortfolioData = (queryClient: QueryClient) =>
  invalidateKeys(queryClient, portfolioDataKeys);

export const reconcileTags = (queryClient: QueryClient) =>
  invalidateKeys(queryClient, [queryKeys.tags, queryKeys.overview]);

export const reconcileWatchlist = (queryClient: QueryClient) =>
  invalidateKeys(queryClient, [queryKeys.watchlist, queryKeys.triggeredAlerts]);
