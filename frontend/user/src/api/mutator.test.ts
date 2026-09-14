import { describe, it, expect, vi, beforeEach } from 'vitest';

const spies = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  del: vi.fn(),
};

vi.mock('@portfolio/shared', () => ({
  createApi: () => spies,
}));

const { mutator } = await import('src/api/mutator');

describe('orval mutator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('sends query params for GET', async () => {
    await mutator({ method: 'get', url: '/x', params: { page: 2 } });

    expect(spies.get).toHaveBeenCalledWith('/x', { params: { page: 2 }, headers: undefined });
  });

  it('normalizes uppercase methods', async () => {
    await mutator({ method: 'GET', url: '/x' });

    expect(spies.get).toHaveBeenCalled();
  });

  it('passes body as the second argument for POST/PUT/PATCH', async () => {
    await mutator({ method: 'post', url: '/x', data: { a: 1 }, params: { q: 'z' } });
    await mutator({ method: 'put', url: '/x', data: { a: 1 }, params: { q: 'z' } });
    await mutator({ method: 'patch', url: '/x', data: { a: 1 }, params: { q: 'z' } });

    expect(spies.post).toHaveBeenCalledWith('/x', { a: 1 }, { params: { q: 'z' }, headers: undefined });
    expect(spies.put).toHaveBeenCalledWith('/x', { a: 1 }, { params: { q: 'z' }, headers: undefined });
    expect(spies.patch).toHaveBeenCalledWith('/x', { a: 1 }, { params: { q: 'z' }, headers: undefined });
  });

  it('sends a DELETE body as the second argument, not merged into config', async () => {
    // apiService.del(url, body, config): merging the body into config produced
    // {"params":..,"data":{"currentPassword":..}} on the wire.
    await mutator({ method: 'delete', url: '/x', data: { currentPassword: 'pw' }, params: { q: 'z' } });

    expect(spies.del).toHaveBeenCalledWith('/x', { currentPassword: 'pw' }, { params: { q: 'z' }, headers: undefined });
  });

  it('omits the body for bodyless DELETE', async () => {
    await mutator({ method: 'delete', url: '/x' });

    expect(spies.del).toHaveBeenCalledWith('/x', { params: undefined, headers: undefined });
  });
});
