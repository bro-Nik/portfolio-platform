import { describe, it, expect } from 'vitest';
import {
  calculatePortfolioAssetStats,
  calculateWalletAssetStats,
  buildPortfolioStats,
  buildWalletStats,
} from 'src/utils/assetStats';

describe('calculatePortfolioAssetStats', () => {
  it('shows profit for purchased assets', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 2, amount: 100 }, 100);
    expect(stats.costNow).toBe(200);
    expect(stats.invested).toBe(100);
    expect(stats.averagePrice).toBe(50);
    expect(stats.profit).toBe(100);
  });

  it('returns null profit without invested amount and realized profit', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 100, amount: 0 }, 1);
    expect(stats.costNow).toBe(100);
    expect(stats.invested).toBe(0);
    expect(stats.hasBasis).toBe(false);
    expect(stats.profit).toBeNull();
  });

  it('calculates average price over the whole quantity', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 3, amount: 100 }, 100);
    expect(stats.averagePrice).toBeCloseTo(33.33);
    expect(stats.profit).toBe(200);
  });

  it('has basis when realized profit exists even without invested amount', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 0, amount: 0, realizedProfit: 50 }, 100);
    expect(stats.hasBasis).toBe(true);
    expect(stats.profit).toBe(50);
  });

  it('includes realized profit', () => {
    const stats = calculatePortfolioAssetStats(
      { quantity: 1, amount: 100, realizedProfit: 50 },
      200,
    );
    expect(stats.profit).toBe(150);
  });

  it('returns null profit without basis', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 0, amount: 0 }, 100);
    expect(stats.profit).toBeNull();
  });

  it('returns null cost and profit without price', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 2, amount: 100 }, undefined);
    expect(stats.costNow).toBeNull();
    expect(stats.profit).toBeNull();
    expect(stats.hasPrice).toBe(false);
  });

  it('returns null cost and profit when price is not a number', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 2, amount: 100 }, 'abc');
    expect(stats.costNow).toBeNull();
    expect(stats.profit).toBeNull();
  });

  it('shows profit for input basis (Input 10 USDT@1 + Earning 10 USDT)', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 20, amount: 10 }, 1);
    expect(stats.invested).toBe(10);
    expect(stats.profit).toBe(10);
  });

  it('keeps average price from basis even without live price', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 20, amount: 10 }, undefined);
    expect(stats.averagePrice).toBe(0.5);
  });

  it('shows realized profit even without live price', () => {
    const stats = calculatePortfolioAssetStats({ quantity: 0, amount: 0, realizedProfit: 50 }, undefined);
    expect(stats.hasPrice).toBe(false);
    expect(stats.profit).toBe(50);
  });
});

describe('calculateWalletAssetStats', () => {
  it('calculates cost now', () => {
    const stats = calculateWalletAssetStats({ quantity: 5 }, 10);
    expect(stats.costNow).toBe(50);
  });
});

describe('buildPortfolioStats', () => {
  it('aggregates asset stats into portfolio and overall totals', () => {
    const portfolios = [
      { id: 1, isArchived: false, assets: [
        { tickerId: 'a', quantity: 2, amount: 100, buyOrders: 1, sellOrders: 0 },
        { tickerId: 'b', quantity: 5, amount: 50, buyOrders: 2, sellOrders: 0 },
      ] },
      { id: 2, isArchived: false, assets: [
        { tickerId: 'c', quantity: 1, amount: 10, buyOrders: 1, sellOrders: 0 },
      ] },
    ];
    const prices = { a: 100, b: 10, c: 10 };

    const { items, overall } = buildPortfolioStats(portfolios, prices);

    expect(items[0].costNow).toBe(250);
    expect(items[0].invested).toBe(150);
    expect(items[1].costNow).toBe(10);

    expect(overall.totalCostNow).toBe(260);
    expect(overall.totalInvested).toBe(160);
    expect(overall.totalBuyOrders).toBe(4);
    expect(overall.totalCapitalDeployed).toBe(160);
    expect(overall.totalProfit).toBe(100);
  });

  it('computes share of invested per portfolio', () => {
    const portfolios = [
      { id: 1, assets: [{ tickerId: 'a', quantity: 1, amount: 75 }] },
      { id: 2, assets: [{ tickerId: 'b', quantity: 1, amount: 25 }] },
    ];
    const prices = { a: 100, b: 100 };

    const { items } = buildPortfolioStats(portfolios, prices);
    expect(items[0].share).toBeCloseTo(75);
    expect(items[1].share).toBeCloseTo(25);
  });

  it('sets zero share when total invested is zero', () => {
    const { items } = buildPortfolioStats(
      [{ id: 1, assets: [{ tickerId: 'a', quantity: 0, amount: 0 }] }],
      { a: 5 },
    );
    expect(items[0].share).toBe(0);
  });

  it('returns empty result for empty input', () => {
    const { items, overall } = buildPortfolioStats([], {});
    expect(items).toEqual([]);
    expect(overall).toEqual({});
  });
});

describe('buildWalletStats', () => {
  it('aggregates wallet costs and computes share by costNow', () => {
    const wallets = [
      { id: 1, isArchived: false, assets: [{ tickerId: 'a', quantity: 4, buyOrders: 1 }] },
      { id: 2, isArchived: true, assets: [] },
    ];
    const prices = { a: 25 };

    const { items, overall } = buildWalletStats(wallets, prices);

    expect(items[0].costNow).toBe(100);
    expect(items[0].share).toBe(100);
    expect(items[1].share).toBe(0);
    expect(overall.totalCostNow).toBe(100);
    expect(overall.totalBuyOrders).toBe(1);
  });

  it('treats missing price as zero', () => {
    const { items, overall } = buildWalletStats(
      [{ id: 1, assets: [{ tickerId: 'x', quantity: 3 }] }],
      {},
    );
    expect(items[0].assets[0].price).toBe(0);
    expect(overall.totalCostNow).toBe(0);
  });

  it('returns empty result for empty input', () => {
    const { items, overall } = buildWalletStats([], {});
    expect(items).toEqual([]);
    expect(overall).toEqual({});
  });
});
