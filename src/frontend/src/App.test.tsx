import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';

import App from './App';
import { mockUsers } from './test/testUtils';

describe('App', () => {
  beforeEach(() => {
    localStorage.setItem('actingUserId', '1');
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(async (url: string) => {
        if (url.includes('/api/users')) {
          return {
            ok: true,
            headers: { get: () => 'application/json' },
            json: async () => mockUsers,
          };
        }
        if (url.includes('/api/tickets')) {
          return {
            ok: true,
            headers: { get: () => 'application/json' },
            json: async () => ({ items: [], total: 0, page: 1, pageSize: 20 }),
          };
        }
        return { ok: true, json: async () => ({}) };
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it('renders application shell with acting-user disclaimer', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/not authentication/i)).toBeInTheDocument();
    });
    expect(screen.getByLabelText(/select acting user/i)).toBeInTheDocument();
  });
});
