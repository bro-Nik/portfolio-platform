import { describe, it, expect } from 'vitest';
import { shouldRetryQuery, defaultQueryOptions } from '@portfolio/shared';

const errorWithStatus = (status) => ({ response: { status } });

describe('shouldRetryQuery', () => {
  it('does not retry twice', () => {
    expect(shouldRetryQuery(1, errorWithStatus(500))).toBe(false);
  });

  it('retries server errors once', () => {
    expect(shouldRetryQuery(0, errorWithStatus(500))).toBe(true);
    expect(shouldRetryQuery(0, errorWithStatus(502))).toBe(true);
  });

  // React Query по умолчанию повторяет и 4xx: 401/422 уходили в повтор,
  // хотя повтор их не исправляет и только добивает rate limit.
  it.each([400, 401, 403, 404, 422, 429])('does not retry %s', (status) => {
    expect(shouldRetryQuery(0, errorWithStatus(status))).toBe(false);
  });

  it('retries network errors without a response', () => {
    expect(shouldRetryQuery(0, new Error('Network Error'))).toBe(true);
  });
});

describe('defaultQueryOptions', () => {
  // /api/overview сам по себе тяжёлый и rate-limited до 10 запросов в минуту.
  it('does not refetch on window focus', () => {
    expect(defaultQueryOptions.refetchOnWindowFocus).toBe(false);
  });

  it('keeps a finite staleTime', () => {
    expect(defaultQueryOptions.staleTime).toBeGreaterThan(0);
  });
});
