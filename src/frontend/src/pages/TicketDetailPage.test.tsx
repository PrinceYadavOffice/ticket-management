import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ActingUserProvider } from '../context/ActingUserContext';
import TicketDetailPage from '../pages/TicketDetailPage';
import { mockUsers } from '../test/testUtils';

const ticketDetail = {
  id: 5,
  title: 'VPN issue',
  description: 'Disconnects hourly',
  priority: 'High',
  status: 'Open',
  assignedTo: 2,
  createdBy: 1,
  createdAt: '2026-07-20T10:00:00Z',
  updatedAt: '2026-07-20T10:00:00Z',
  creator: mockUsers[0],
  assignee: mockUsers[1],
  comments: [],
  allowedStatusTransitions: ['In Progress', 'Cancelled'],
};

function mockFetchRouter(handler: (url: string, init?: RequestInit) => unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const result = handler(url, init);
      if (result && typeof result === 'object' && 'ok' in result) return result;
      return {
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => result,
      };
    }),
  );
}

function renderDetail() {
  return render(
    <MemoryRouter initialEntries={['/tickets/5']}>
      <ActingUserProvider>
        <Routes>
          <Route path="/tickets/:id" element={<TicketDetailPage />} />
        </Routes>
      </ActingUserProvider>
    </MemoryRouter>,
  );
}

describe('TicketDetailPage', () => {
  beforeEach(() => {
    localStorage.setItem('actingUserId', '1');
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it('updates ticket fields on save', async () => {
    const user = userEvent.setup();
    let patchBody: unknown;

    mockFetchRouter((url, init) => {
      if (url.includes('/api/users')) return mockUsers;
      if (url.includes('/status')) return ticketDetail;
      if (url.includes('/api/tickets/5') && init?.method === 'PATCH') {
        patchBody = JSON.parse(String(init.body));
        return { ...ticketDetail, title: 'Updated VPN issue' };
      }
      if (url.includes('/api/tickets/5')) return ticketDetail;
      return {};
    });

    renderDetail();
    await screen.findByDisplayValue('VPN issue');

    const titleInput = screen.getByLabelText(/title/i);
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated VPN issue');
    await user.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(patchBody).toEqual(
        expect.objectContaining({ title: 'Updated VPN issue' }),
      );
    });
  });

  it('displays rejected transition error and keeps Open status visible', async () => {
    const user = userEvent.setup();

    mockFetchRouter((url, init) => {
      if (url.includes('/api/users')) return mockUsers;
      if (url.includes('/status') && init?.method === 'PATCH') {
        return {
          ok: false,
          status: 409,
          headers: { get: () => 'application/json' },
          json: async () => ({
            error: {
              code: 'INVALID_STATUS_TRANSITION',
              message: "Cannot transition from 'Open' to 'In Progress'",
              details: {},
            },
          }),
        };
      }
      if (url.includes('/api/tickets/5')) return ticketDetail;
      return {};
    });

    renderDetail();
    await screen.findByRole('button', { name: /move to in progress/i });

    await user.click(screen.getByRole('button', { name: /move to in progress/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        "Cannot transition from 'Open' to 'In Progress'",
      );
    });
    expect(screen.getByText('Open', { selector: '.badge' })).toBeInTheDocument();
  });

  it('submits comment with X-User-Id', async () => {
    const user = userEvent.setup();
    let commentHeaders: Record<string, string> | undefined;

    mockFetchRouter((url, init) => {
      if (url.includes('/api/users')) return mockUsers;
      if (url.includes('/comments') && init?.method === 'POST') {
        commentHeaders = init.headers as Record<string, string>;
        return {
          id: 1,
          ticketId: 5,
          message: 'Checking logs',
          createdAt: '2026-07-20T11:00:00Z',
          createdBy: mockUsers[0],
        };
      }
      if (url.includes('/api/tickets/5')) {
        if (init?.method === 'PATCH') return ticketDetail;
        return {
          ...ticketDetail,
          comments: commentHeaders
            ? [
                {
                  id: 1,
                  ticketId: 5,
                  message: 'Checking logs',
                  createdAt: '2026-07-20T11:00:00Z',
                  createdBy: mockUsers[0],
                },
              ]
            : ticketDetail.comments,
        };
      }
      return {};
    });

    renderDetail();
    await screen.findByDisplayValue('VPN issue');

    await user.type(screen.getByLabelText(/add comment/i), 'Checking logs');
    await user.click(screen.getByRole('button', { name: /post comment/i }));

    await waitFor(() => {
      expect(commentHeaders?.['X-User-Id']).toBe('1');
      expect(screen.getByText('Checking logs')).toBeInTheDocument();
    });
  });
});
