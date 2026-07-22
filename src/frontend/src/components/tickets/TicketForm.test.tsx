import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import TicketForm, { validateTicketForm } from './TicketForm';
import { mockUsers } from '../../test/testUtils';

describe('validateTicketForm', () => {
  it('requires title and description', () => {
    const errors = validateTicketForm({
      title: '  ',
      description: '',
      priority: 'Low',
      assignedTo: '',
    });
    expect(errors.title).toBeDefined();
    expect(errors.description).toBeDefined();
  });
});

describe('TicketForm', () => {
  it('shows client validation for required fields', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<TicketForm mode="create" users={mockUsers} onSubmit={onSubmit} />);

    await user.click(screen.getByRole('button', { name: /create ticket/i }));
    expect(screen.getByText('Title is required')).toBeInTheDocument();
    expect(screen.getByText('Description is required')).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('submits valid payload', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<TicketForm mode="create" users={mockUsers} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/title/i), 'New bug');
    await user.type(screen.getByLabelText(/description/i), 'Steps to reproduce');
    await user.click(screen.getByRole('button', { name: /create ticket/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'New bug',
      description: 'Steps to reproduce',
      priority: 'Medium',
      assignedTo: null,
    });
  });

  it('displays API field errors', () => {
    render(
      <TicketForm
        mode="create"
        users={mockUsers}
        onSubmit={vi.fn()}
        fieldErrors={{ title: 'Title already exists' }}
      />,
    );
    expect(screen.getByText('Title already exists')).toBeInTheDocument();
  });
});
