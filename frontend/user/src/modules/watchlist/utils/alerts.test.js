import { describe, expect, it } from 'vitest';
import { deriveDirection, distanceToTarget, isTriggered } from './alerts';

describe('deriveDirection', () => {
  it('returns below when target is under current price', () => {
    expect(deriveDirection(60000, 50000)).toBe('below');
  });

  it('returns above when target is over current price', () => {
    expect(deriveDirection(60000, 70000)).toBe('above');
  });

  it('returns null on missing data', () => {
    expect(deriveDirection(null, 50000)).toBeNull();
    expect(deriveDirection(60000, 0)).toBeNull();
    expect(deriveDirection(0, 50000)).toBeNull();
  });
});

describe('distanceToTarget', () => {
  it('returns 0 when already crossed', () => {
    expect(distanceToTarget(70000, 60000, 'above')).toBe(0);
    expect(distanceToTarget(50000, 60000, 'below')).toBe(0);
  });

  it('returns relative distance otherwise', () => {
    expect(distanceToTarget(60000, 66000, 'above')).toBeCloseTo(0.1);
    expect(distanceToTarget(60000, 54000, 'below')).toBeCloseTo(0.1);
  });

  it('returns null on bad input', () => {
    expect(distanceToTarget(60000, 66000, 'sideways')).toBeNull();
    expect(distanceToTarget(0, 66000, 'above')).toBeNull();
  });
});

describe('isTriggered', () => {
  it('detects triggered alerts', () => {
    expect(isTriggered({ isActive: false, triggeredAt: '2026-01-01' })).toBe(true);
    expect(isTriggered({ isActive: true, triggeredAt: null })).toBe(false);
    expect(isTriggered(null)).toBe(false);
  });
});
