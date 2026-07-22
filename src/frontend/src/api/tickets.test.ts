import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';

import { buildQuery } from '../api/tickets';
import { apiRequest, setActingUserIdProvider } from '../api/client';

describe('apiRequest acting user header', () => {
  beforeEach(() => {
    setActingUserIdProvider(() => 42);
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ items: [], total: 0, page: 1, pageSize: 20 }),
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    setActingUserIdProvider(() => null);
  });

  it('sends X-User-Id when requireActingUser is true', async () => {
    await apiRequest('/api/tickets', {
      method: 'POST',
      body: { title: 't', description: 'd', priority: 'Low' },
      requireActingUser: true,
    });
    const [, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(init.headers['X-User-Id']).toBe('42');
  });

  it('does not require acting user for list requests', async () => {
    await apiRequest('/api/tickets');
    const [, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(init.headers['X-User-Id']).toBe('42');
  });
});

describe('buildQuery', () => {
  it('constructs filter query parameters', () => {
    const query = buildQuery({
      q: 'login',
      status: 'Open',
      priority: 'High',
      assignedTo: 2,
      page: 2,
      pageSize: 10,
    });
    expect(query).toContain('q=login');
    expect(query).toContain('status=Open');
    expect(query).toContain('priority=High');
    expect(query).toContain('assignedTo=2');
    expect(query).toContain('page=2');
    expect(query).toContain('pageSize=10');
  });

  it('includes unassigned filter', () => {
    const query = buildQuery({ unassigned: true, page: 1, pageSize: 20 });
    expect(query).toContain('unassigned=true');
  });
});
