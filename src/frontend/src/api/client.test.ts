import { afterEach, describe, expect, it, vi } from 'vitest';

import { ApiError, NetworkError, apiRequest } from './client';

describe('apiRequest', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('throws NetworkError when fetch fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await expect(apiRequest('/api/users')).rejects.toBeInstanceOf(NetworkError);
  });

  it('throws ApiError for malformed JSON error responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        headers: { get: () => 'application/json' },
        text: async () => 'not-json',
      }),
    );

    await expect(apiRequest('/api/tickets')).rejects.toBeInstanceOf(ApiError);
  });
});
