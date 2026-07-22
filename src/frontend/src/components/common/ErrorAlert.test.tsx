import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import ErrorAlert from './ErrorAlert';
import { ApiError } from '../../api/client';

describe('ErrorAlert', () => {
  it('displays API error message and field details', () => {
    const error = new ApiError(422, {
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Request validation failed',
        details: { fields: { title: 'Title is required' } },
      },
    });
    render(<ErrorAlert error={error} />);
    expect(screen.getByRole('alert')).toHaveTextContent('Request validation failed');
    expect(screen.getByText(/Title is required/)).toBeInTheDocument();
  });
});
