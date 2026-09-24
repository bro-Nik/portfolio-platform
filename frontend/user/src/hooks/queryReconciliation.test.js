import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient } from '@tanstack/react-query';

import { reconcilePortfolioData, reconcileTags, queryKeys } from '@portfolio/shared';

const makeClient = () => {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  client.invalidateQueries = vi.fn().mockResolvedValue([]);
  return client;
};

describe('reconcilePortfolioData', () => {
  let client;

  beforeEach(() => {
    client = makeClient();
  });

  it('invalidates every key that depends on portfolio data', () => {
    reconcilePortfolioData(client);

    const keys = client.invalidateQueries.mock.calls.map(([arg]) => arg.queryKey);
    expect(keys).toEqual(expect.arrayContaining([
      queryKeys.overview,
      queryKeys.portfolioAssetTransactions,
      queryKeys.walletAssetTransactions,
      queryKeys.assetPrices,
    ]));
  });

  it('does not invalidate unrelated keys', () => {
    reconcilePortfolioData(client);

    const keys = client.invalidateQueries.mock.calls.map(([arg]) => arg.queryKey);
    expect(keys).not.toContainEqual(queryKeys.sessions);
    expect(keys).not.toContainEqual(queryKeys.profile);
  });
});

describe('reconcileTags', () => {
  it('invalidates tags and overview', () => {
    const client = makeClient();

    reconcileTags(client);

    const keys = client.invalidateQueries.mock.calls.map(([arg]) => arg.queryKey);
    expect(keys).toEqual([queryKeys.tags, queryKeys.overview]);
  });
});

describe('queryKeys', () => {
  it('are stable identities', () => {
    // Мутации полагаются на сравнение по ссылке во время оптимистичных правок.
    expect(queryKeys.overview).toEqual(['overview']);
    expect(queryKeys.portfolioAssetTransactions).toEqual(['portfolioAssetTransactions']);
  });
});
