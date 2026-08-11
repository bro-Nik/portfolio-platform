import { describe, it, expect, beforeEach } from 'vitest';
import { formatCurrency, formatCurrencyFromUsd, formatPercentage, formatProfit, formatQuantity } from 'src/utils/format';
import { usePreferencesStore } from 'src/stores/preferencesStore';
import { fromUsd, toUsd } from 'src/utils/currency';

describe('format utils', () => {
  beforeEach(() => {
    usePreferencesStore.setState({ displayCurrency: 'USD', rates: {} });
  });

  it('formats currency', () => {
    expect(formatCurrency(1234.5)).toContain('234,50');
    expect(formatCurrency(1234.5)).toContain('$');
  });

  it('returns dash for missing currency values', () => {
    expect(formatCurrency(null)).toBe('-');
    expect(formatCurrency(undefined)).toBe('-');
    expect(formatCurrency(NaN)).toBe('-');
    expect(formatCurrency(0)).toContain('0,00');
  });

  it('converts from USD to display currency and back', () => {
    usePreferencesStore.setState({ displayCurrency: 'RUB', rates: { RUB: 0.011 } });
    expect(fromUsd(110)).toBeCloseTo(10000);
    expect(toUsd(10000)).toBeCloseTo(110);
  });

  it('returns null unchanged when converting', () => {
    expect(fromUsd(null)).toBeNull();
    expect(toUsd(undefined)).toBeUndefined();
  });

  it('falls back to rate 1 when rate is missing', () => {
    usePreferencesStore.setState({ displayCurrency: 'EUR', rates: {} });
    expect(fromUsd(100)).toBe(100);
  });

  it('formats from USD in display currency', () => {
    usePreferencesStore.setState({ displayCurrency: 'RUB', rates: { RUB: 0.011 } });
    const formatted = formatCurrencyFromUsd(110);
    expect(formatted).toContain('₽');
    expect(formatted).toContain('10');
    expect(formatted).not.toContain('$');
  });

  it('formats percentage', () => {
    expect(formatPercentage(12.345, 1)).toBe('12.3%');
  });

  it('formats profit with percentage', () => {
    expect(formatProfit(500, 1000, 1000)).toContain('500');
    expect(formatProfit(500, 1000, 1000)).toContain('(50%)');
  });

  it('returns undefined for null profit', () => {
    expect(formatProfit(null, 100, 100)).toBeUndefined();
  });

  it('formats quantity without scientific notation', () => {
    expect(formatQuantity('0E-20')).toBe('0');
    expect(formatQuantity('0.00000000000000000000')).toBe('0');
    expect(formatQuantity(0)).toBe('0');
    expect(formatQuantity(null)).toBe('0');
    expect(formatQuantity(undefined)).toBe('0');
    expect(formatQuantity('0.05000132323')).toBe('0,05000132323');
    expect(formatQuantity('0.0015923962068690731')).not.toContain('E');
  });
});
