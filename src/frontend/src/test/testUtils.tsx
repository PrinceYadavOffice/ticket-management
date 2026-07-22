import { render, type RenderOptions } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

import { ActingUserProvider } from '../context/ActingUserContext';
import type { User } from '../api/types';

export const mockUsers: User[] = [
  { id: 1, name: 'Alice Chen', email: 'alice@test.example', role: 'Agent' },
  { id: 2, name: 'Bob Martinez', email: 'bob@test.example', role: 'Admin' },
];

export function mockFetchUsers() {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockUsers,
    }),
  );
}

export function renderWithProviders(
  ui: React.ReactElement,
  { route = '/', path = '/' }: { route?: string; path?: string } = {},
  options?: RenderOptions,
) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <ActingUserProvider>
        <Routes>
          <Route path={path} element={ui} />
        </Routes>
      </ActingUserProvider>
    </MemoryRouter>,
    options,
  );
}
