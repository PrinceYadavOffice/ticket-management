import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';

describe('App', () => {
  it('renders the application title', () => {
    render(<App />);
    expect(
      screen.getByRole('heading', { name: /support ticket management system/i }),
    ).toBeInTheDocument();
  });

  it('displays acting-user disclaimer', () => {
    render(<App />);
    expect(screen.getByText(/not authentication/i)).toBeInTheDocument();
  });
});
