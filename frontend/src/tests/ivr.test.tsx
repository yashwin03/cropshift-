import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import IvrPage from '../pages/IvrPage';

const renderIvrPage = () =>
  render(
    <MemoryRouter>
      <IvrPage />
    </MemoryRouter>
  );

describe('IvrPage — Mobile Voice Advisory & Slide-to-Call Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders Voice Advisory header and offline accessibility badges', () => {
    renderIvrPage();

    expect(screen.getByRole('heading', { level: 1, name: /voice advisory/i })).toBeInTheDocument();
    expect(screen.getByText(/works without internet/i)).toBeInTheDocument();
    expect(
      screen.getByText(/get crop advice through a phone call, even when internet is unavailable/i)
    ).toBeInTheDocument();

    // Three capability cards
    expect(screen.getAllByText(/crop recommendation/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/get crop guidance through the ivr/i)).toBeInTheDocument();
    expect(screen.getAllByText(/market prices/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/hear the predefined market-price information/i)).toBeInTheDocument();
    expect(screen.getAllByText(/government schemes/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/hear available demo scheme information/i)).toBeInTheDocument();



    // Direct phone link
    expect(screen.getByRole('link', { name: /call 09513886363/i })).toHaveAttribute(
      'href',
      'tel:09513886363'
    );
    expect(screen.getByText(/PIN: 8618-8551-17/i)).toBeInTheDocument();
  });

  test('slide activation triggers phone call action and displays clear feedback state', () => {
    renderIvrPage();

    const slider = screen.getByRole('slider');
    expect(slider).toBeInTheDocument();

    // Trigger slide to completion
    fireEvent.keyDown(slider, { key: 'ArrowRight' });

    // Feedback state appears
    expect(screen.getByTestId('call-triggered-feedback')).toBeInTheDocument();
    expect(screen.getByText(/phone dialer triggered/i)).toBeInTheDocument();
    expect(screen.getAllByText(/09513886363/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole('link', { name: /dial again/i })).toHaveAttribute('href', 'tel:09513886363');

    // Reset control restores slider
    const resetBtn = screen.getByRole('button', { name: /reset control/i });
    fireEvent.click(resetBtn);

    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  test('renders connectivity section explaining online vs offline capabilities', () => {
    renderIvrPage();

    const connectivitySection = screen.getByTestId('connectivity-info');
    expect(connectivitySection).toBeInTheDocument();
    expect(screen.getByText(/available without internet/i)).toBeInTheDocument();
    expect(screen.getByText(/requires internet/i)).toBeInTheDocument();
    expect(screen.getByText(/voice advisory by phone/i)).toBeInTheDocument();
  });
});

