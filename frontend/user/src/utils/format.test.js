import { describe, it, expect } from 'vitest';
import { formatCurrency, formatPercentage, formatProfit } from 'src/utils/format';

describe('format utils', () => {
  it('formats currency', () => {
    expect(formatCurrency(1234.5)).toContain('234,50');
    expect(formatCurrency(1234.5)).toContain('$');
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
});
