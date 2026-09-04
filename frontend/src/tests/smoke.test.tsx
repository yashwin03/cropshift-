import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App Smoke Test', () => {
  it('renders the default layout with farmer greetings text for authenticated farmer', () => {
    localStorage.setItem('token', 'valid-mock-token');
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'Rajesh', role: 'FARMER' }));

    render(<App />);
    expect(screen.getAllByText(/Welcome/i).length).toBeGreaterThan(0);
  });
});

