import { describe, it, expect } from 'vitest';
import { formatCurrency, formatPercentage, formatProfit, formatQuantity } from 'src/utils/format';

describe('format utils', () => {
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
