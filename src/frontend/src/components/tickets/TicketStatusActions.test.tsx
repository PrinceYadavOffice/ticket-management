import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import TicketStatusActions from './TicketStatusActions';
import { ApiError } from '../../api/client';

describe('TicketStatusActions', () => {
  it('shows allowed transition buttons for Open', () => {
    render(
      <TicketStatusActions
        currentStatus="Open"
        allowedTransitions={['In Progress', 'Cancelled']}
        onTransition={vi.fn()}
      />,
    );
    expect(screen.getByRole('button', { name: /move to in progress/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /move to cancelled/i })).toBeInTheDocument();
  });

  it('shows no actions for terminal Closed status', () => {
    render(
      <TicketStatusActions
        currentStatus="Closed"
        allowedTransitions={[]}
        onTransition={vi.fn()}
      />,
    );
    expect(screen.queryByRole('button', { name: /move to/i })).not.toBeInTheDocument();
    expect(screen.getByText(/no status actions available/i)).toBeInTheDocument();
  });

  it('shows no actions for terminal Cancelled status', () => {
    render(
      <TicketStatusActions
        currentStatus="Cancelled"
        allowedTransitions={[]}
        onTransition={vi.fn()}
      />,
    );
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('displays rejected transition error from backend', () => {
    const err = new ApiError(409, {
      error: {
        code: 'INVALID_STATUS_TRANSITION',
        message: 'Cannot transition from Open to Resolved',
        details: {},
      },
    });
    render(
      <TicketStatusActions
        currentStatus="Open"
        allowedTransitions={['In Progress']}
        onTransition={vi.fn()}
        error={err}
      />,
    );
    expect(screen.getByRole('alert')).toHaveTextContent('Cannot transition from Open to Resolved');
  });

  it('calls onTransition when button clicked', async () => {
    const user = userEvent.setup();
    const onTransition = vi.fn();
    render(
      <TicketStatusActions
        currentStatus="In Progress"
        allowedTransitions={['Resolved', 'Cancelled']}
        onTransition={onTransition}
      />,
    );
    await user.click(screen.getByRole('button', { name: /move to resolved/i }));
    expect(onTransition).toHaveBeenCalledWith('Resolved');
  });
});
