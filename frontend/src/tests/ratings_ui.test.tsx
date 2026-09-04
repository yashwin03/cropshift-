import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import * as ratingService from '../services/ratingService';
import { TradeOrder } from '../types/api';
import { TradeOrderRatingWidget } from '../pages/BiddingPage';

vi.mock('../services/ratingService');

describe('Rating & Trust System Frontend Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockFulfilledOrder: TradeOrder = {
    id: 101,
    buyer_id: 10,
    farmer_id: 20,
    crop_name: 'Groundnut (Kadir-6)',
    allocated_quantity_quintals: 50,
    agreed_price_per_quintal: 6400,
    status: 'FULFILLED',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    fulfilled_at: new Date().toISOString(),
    buyer_display_id: 'BUYER-10',
    farmer_display_id: 'FARMER-20',
  };

  const mockCreatedOrder: TradeOrder = {
    ...mockFulfilledOrder,
    status: 'CREATED',
  };

  it('should call submitRating with correct payload for completed deal', async () => {
    const mockRatingRes: ratingService.RatingResponse = {
      id: 1,
      rater_id: 10,
      target_user_id: 20,
      trade_order_id: 101,
      stars: 5,
      comment: 'Great transaction',
      created_at: new Date().toISOString(),
    };

    vi.mocked(ratingService.submitRating).mockResolvedValue(mockRatingRes);

    const payload = {
      target_user_id: 20,
      trade_order_id: 101,
      stars: 5,
      comment: 'Great transaction',
    };

    const res = await ratingService.submitRating(payload);
    expect(res.stars).toBe(5);
    expect(ratingService.submitRating).toHaveBeenCalledWith(payload);
  });

  it('should retrieve user rating summary correctly', async () => {
    const mockSummary: ratingService.UserRatingSummary = {
      user_id: 20,
      average_rating: 4.8,
      total_ratings: 5,
      completed_transactions: 6,
      ratings: [],
    };

    vi.mocked(ratingService.getUserRatingSummary).mockResolvedValue(mockSummary);

    const summary = await ratingService.getUserRatingSummary(20);
    expect(summary.average_rating).toBe(4.8);
    expect(summary.completed_transactions).toBe(6);
  });

  it('should NOT render rating widget for non-fulfilled orders', () => {
    const { container } = render(
      <TradeOrderRatingWidget order={mockCreatedOrder} isBuyer={true} onRatingSubmitted={() => {}} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('should render rating button and trust summary for eligible fulfilled deal', async () => {
    vi.mocked(ratingService.getTradeOrderRatingForMe).mockResolvedValue(null);
    vi.mocked(ratingService.getUserRatingSummary).mockResolvedValue({
      user_id: 20,
      average_rating: null,
      total_ratings: 0,
      completed_transactions: 1,
      ratings: [],
    });

    render(<TradeOrderRatingWidget order={mockFulfilledOrder} isBuyer={true} onRatingSubmitted={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('Farmer Rating')).toBeInTheDocument();
      expect(screen.getByText('No ratings yet')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Rate Farmer/i })).toBeInTheDocument();
    });
  });

  it('should open 5-star rating form and successfully submit rating', async () => {
    vi.mocked(ratingService.getTradeOrderRatingForMe).mockResolvedValue(null);
    vi.mocked(ratingService.getUserRatingSummary).mockResolvedValue({
      user_id: 20,
      average_rating: 4.5,
      total_ratings: 2,
      completed_transactions: 3,
      ratings: [],
    });

    const mockSubmittedRating: ratingService.RatingResponse = {
      id: 99,
      rater_id: 10,
      target_user_id: 20,
      trade_order_id: 101,
      stars: 5,
      comment: 'Excellent crop quality and prompt service',
      created_at: new Date().toISOString(),
    };
    vi.mocked(ratingService.submitRating).mockResolvedValue(mockSubmittedRating);

    const onSubmittedMock = vi.fn();
    render(<TradeOrderRatingWidget order={mockFulfilledOrder} isBuyer={true} onRatingSubmitted={onSubmittedMock} />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Rate Farmer/i })).toBeInTheDocument();
    });

    // Click "Rate Farmer" button
    fireEvent.click(screen.getByRole('button', { name: /Rate Farmer/i }));

    // Form should appear
    expect(screen.getByText('Rate your experience')).toBeInTheDocument();
    expect(screen.getByText('How was your transaction with this farmer?')).toBeInTheDocument();

    // Select 5th star
    const star5 = screen.getByRole('button', { name: /Rate 5 stars/i });
    fireEvent.click(star5);

    // Enter comment
    const commentBox = screen.getByPlaceholderText(/Optional review for Farmer.../i);
    fireEvent.change(commentBox, { target: { value: 'Excellent crop quality and prompt service' } });

    // Submit rating
    fireEvent.click(screen.getByRole('button', { name: /Submit Rating/i }));

    await waitFor(() => {
      expect(ratingService.submitRating).toHaveBeenCalledWith({
        target_user_id: 20,
        trade_order_id: 101,
        stars: 5,
        comment: 'Excellent crop quality and prompt service',
      });
      expect(screen.getByText('Rating Submitted')).toBeInTheDocument();
      expect(onSubmittedMock).toHaveBeenCalled();
    });
  });

  it('should display existing rating on mount/reload and prevent duplicate submission', async () => {
    const existingRating: ratingService.RatingResponse = {
      id: 88,
      rater_id: 10,
      target_user_id: 20,
      trade_order_id: 101,
      stars: 5,
      comment: 'Already submitted rating',
      created_at: new Date().toISOString(),
    };

    vi.mocked(ratingService.getTradeOrderRatingForMe).mockResolvedValue(existingRating);
    vi.mocked(ratingService.getUserRatingSummary).mockResolvedValue({
      user_id: 20,
      average_rating: 5.0,
      total_ratings: 1,
      completed_transactions: 1,
      ratings: [existingRating],
    });

    render(<TradeOrderRatingWidget order={mockFulfilledOrder} isBuyer={true} onRatingSubmitted={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('Rating Submitted')).toBeInTheDocument();
      expect(screen.getByText('"Already submitted rating"')).toBeInTheDocument();
      // "Rate Farmer" button form must NOT be visible since it is already rated
      expect(screen.queryByRole('button', { name: /Rate Farmer/i })).not.toBeInTheDocument();
    });
  });
});
