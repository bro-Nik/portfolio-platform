import { describe, it, expect } from 'vitest';
import { calculatePortfolioAssetStats, calculateWalletAssetStats } from 'src/utils/assetStats';

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
});

describe('calculateWalletAssetStats', () => {
  it('calculates cost now', () => {
    const stats = calculateWalletAssetStats({ quantity: 5 }, 10);
    expect(stats.costNow).toBe(50);
  });
});
