import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import TicketList from './TicketList';
import type { Ticket } from '../../api/types';
import { mockUsers } from '../../test/testUtils';

const tickets: Ticket[] = [
  {
    id: 1,
    title: 'Login issue',
    description: 'Cannot sign in',
    priority: 'High',
    status: 'Open',
    assignedTo: 2,
    createdBy: 1,
    createdAt: '2026-07-20T10:00:00Z',
    updatedAt: '2026-07-20T10:00:00Z',
  },
];

describe('TicketList', () => {
  it('renders persisted tickets in a table', () => {
    render(
      <MemoryRouter>
        <TicketList tickets={tickets} users={mockUsers} />
      </MemoryRouter>,
    );
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Login issue' })).toHaveAttribute(
      'href',
      '/tickets/1',
    );
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Bob Martinez')).toBeInTheDocument();
  });
});
