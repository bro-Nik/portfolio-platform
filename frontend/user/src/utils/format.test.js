import { describe, it, expect, beforeEach } from 'vitest';
import { formatCurrency, formatCurrencyFromUsd, formatPercentage, formatProfit, formatQuantity } from 'src/utils/format';
import { usePreferencesStore } from 'src/stores/preferencesStore';
import { fromUsd, toUsd } from 'src/utils/currency';

describe('format utils', () => {
  beforeEach(() => {
    usePreferencesStore.setState({ displayCurrency: 'USD', rates: {} });
  });

  it('formats currency', () => {
    expect(formatCurrency(1234.5)).toMatch(/1\s?234/);
    expect(formatCurrency(1234.5)).toContain('$');
  });

  it('floors to whole units by default', () => {
    expect(formatCurrency(110.56)).toContain('110');
    expect(formatCurrency(110.56)).not.toContain('111');
    expect(formatCurrency(1.99)).toContain('1');
    expect(formatCurrency(1.99)).not.toContain('2');
    expect(formatCurrency(0.5)).toContain('0');
  });

  it('keeps exact digits with dontRound', () => {
    expect(formatCurrency(110.56, 'USD', 'ru-RU', true)).toContain('110,56');
    expect(formatCurrency(110.56, 'USD', 'ru-RU', true)).toContain('$');
  });

  it('returns dash for missing currency values', () => {
    expect(formatCurrency(null)).toBe('-');
    expect(formatCurrency(undefined)).toBe('-');
    expect(formatCurrency(NaN)).toBe('-');
    expect(formatCurrency(0)).toContain('0');
    expect(formatCurrency(0)).toContain('$');
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
    expect(formatted).toMatch(/10\s?000/);
    expect(formatted).not.toContain('$');
  });

  it('rounds converted values, floors below 1 USD, keeps exact with dontRound', () => {
    usePreferencesStore.setState({ displayCurrency: 'RUB', rates: { RUB: 0.011 } });
    expect(formatCurrencyFromUsd(110.56)).toMatch(/10\s?051/);
    expect(formatCurrencyFromUsd(110.56)).not.toMatch(/10\s?050/);
    expect(formatCurrencyFromUsd(110.56, true)).toMatch(/10\s?050,90/);
  });

  it('floors values below 1 USD regardless of display currency', () => {
    expect(formatCurrencyFromUsd(0.99)).toContain('0');
    expect(formatCurrencyFromUsd(0.99)).not.toContain('1');
    expect(formatCurrencyFromUsd(0.6)).toContain('0');
    expect(formatCurrencyFromUsd(0.6)).not.toContain('1');
    expect(formatCurrencyFromUsd(1.5)).toContain('2');
    expect(formatCurrencyFromUsd(1.1)).toContain('1');
  });

  it('rounds negative values instead of flooring', () => {
    expect(formatCurrencyFromUsd(-0.4)).toContain('0');
    expect(formatCurrencyFromUsd(-0.4)).not.toContain('-0');
    expect(formatCurrencyFromUsd(-0.4)).not.toContain('1');
    expect(formatCurrencyFromUsd(-123.45)).toContain('123');
    expect(formatCurrencyFromUsd(-123.45)).not.toContain('124');
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
