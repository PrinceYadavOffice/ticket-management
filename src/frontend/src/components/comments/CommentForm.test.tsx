import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import CommentForm from './CommentForm';

describe('CommentForm', () => {
  it('shows validation error for blank comment', async () => {
    const user = userEvent.setup();
    render(<CommentForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /post comment/i }));

    expect(screen.getByRole('alert')).toHaveTextContent('Comment cannot be blank');
  });

  it('keeps message when submit handler rejects', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockRejectedValue(new Error('Server error'));

    render(<CommentForm onSubmit={onSubmit} error="Server error" />);

    await user.type(screen.getByLabelText(/add comment/i), 'Retry me');
    await user.click(screen.getByRole('button', { name: /post comment/i }));

    expect(onSubmit).toHaveBeenCalledWith('Retry me');
    expect(screen.getByLabelText(/add comment/i)).toHaveValue('Retry me');
  });

  it('clears message after successful submit', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(<CommentForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/add comment/i), 'Posted');
    await user.click(screen.getByRole('button', { name: /post comment/i }));

    expect(screen.getByLabelText(/add comment/i)).toHaveValue('');
  });
});
