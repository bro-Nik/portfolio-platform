import { describe, it, expect } from 'vitest';
import { formatCurrency, formatPercentage } from 'src/utils/format';

describe('format utils', () => {
  it('formats currency', () => {
    expect(formatCurrency(1234.5)).toContain('234,50');
    expect(formatCurrency(1234.5)).toContain('$');
  });

  it('formats percentage', () => {
    expect(formatPercentage(12.345, 1)).toBe('12.3%');
  });
});
