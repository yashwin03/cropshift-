import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { AuthProvider } from '../contexts/AuthContext';
import StatusBadge from '../components/common/StatusBadge';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import LoadingCard from '../components/common/LoadingCard';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import MainLayout from '../layouts/MainLayout';

describe('Common Components Tests', () => {
  
  describe('Button Component', () => {
    it('renders with children text', () => {
      render(<Button>Click Me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('handles click events', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);
      fireEvent.click(screen.getByRole('button', { name: /click me/i }));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('is disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled Button</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('shows loading spinner and is disabled when isLoading is true', () => {
      render(<Button isLoading>Submit</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
      expect(screen.getByRole('button').querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Badge Component', () => {
    it('renders children correctly', () => {
      render(<Badge>Success Label</Badge>);
      expect(screen.getByText('Success Label')).toBeInTheDocument();
    });

    it('applies styling corresponding to variants', () => {
      const { container } = render(<Badge variant="danger">Error</Badge>);
      expect(container.firstChild).toHaveClass('bg-red-100');
    });
  });

  describe('StatusBadge Component', () => {
    it('translates DataStatus enums and applies correct styling', () => {
      const { container, rerender } = render(<StatusBadge status="REAL" />);
      expect(screen.getByText('Live Data')).toBeInTheDocument();
      expect(container.firstChild).toHaveClass('bg-green-100');

      rerender(<StatusBadge status="DEMO" />);
      expect(screen.queryByText('Verified Model Data')).not.toBeInTheDocument();
      expect(container.firstChild).toHaveClass('bg-amber-100');
    });
  });

  describe('Card Component', () => {
    it('renders header details and children content', () => {
      render(
        <Card title="Test Card" subtitle="Test Subtitle" footer={<button>Footer Action</button>}>
          <p>Card content paragraph</p>
        </Card>
      );
      expect(screen.getByText('Test Card')).toBeInTheDocument();
      expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
      expect(screen.getByText('Card content paragraph')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /footer action/i })).toBeInTheDocument();
    });
  });

  describe('Spinner and LoadingCard Components', () => {
    it('renders spinner elements', () => {
      render(<Spinner />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('renders skeleton items inside LoadingCard', () => {
      const { container } = render(<LoadingCard lines={4} />);
      expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
    });
  });

  describe('ErrorState Component', () => {
    it('renders title, message and fires retry callback', () => {
      const handleRetry = vi.fn();
      render(<ErrorState title="Oops" message="Could not fetch data" onRetry={handleRetry} />);
      expect(screen.getByText('Oops')).toBeInTheDocument();
      expect(screen.getByText('Could not fetch data')).toBeInTheDocument();
      
      const retryBtn = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(retryBtn);
      expect(handleRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('EmptyState Component', () => {
    it('renders title, description and triggers custom action', () => {
      const handleAction = vi.fn();
      render(
        <EmptyState
          title="No farm recorded"
          message="Please add your first farm to run analyses."
          actionLabel="Add Farm"
          onAction={handleAction}
        />
      );
      expect(screen.getByText('No farm recorded')).toBeInTheDocument();
      expect(screen.getByText('Please add your first farm to run analyses.')).toBeInTheDocument();
      
      const actionBtn = screen.getByRole('button', { name: /add farm/i });
      fireEvent.click(actionBtn);
      expect(handleAction).toHaveBeenCalledTimes(1);
    });
  });

  describe('MainLayout Component', () => {
    it('contains brand logo, navigation links, and footer links', () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <MainLayout>
              <div>Main Content Container</div>
            </MainLayout>
          </AuthProvider>
        </BrowserRouter>
      );
      
      // Logo and Branding
      expect(screen.getByText('Crop')).toBeInTheDocument();
      expect(screen.getByText('Shift')).toBeInTheDocument();
      
      // Main desktop navigation links
      expect(screen.getAllByRole('link', { name: /home/i }).length).toBeGreaterThan(0);
      expect(screen.getAllByRole('link', { name: /profit/i }).length).toBeGreaterThan(0);
      expect(screen.getAllByRole('link', { name: /market/i }).length).toBeGreaterThan(0);
      expect(screen.getAllByRole('link', { name: /map/i }).length).toBeGreaterThan(0);
      expect(screen.getAllByRole('link', { name: /subsidies/i }).length).toBeGreaterThan(0);


      
      // Main viewport text content
      expect(screen.getByText('Main Content Container')).toBeInTheDocument();
      
      // Footer text content
      expect(screen.getByText(/CropShift/)).toBeInTheDocument();

      // Login button or link in header
      const loginElements = screen.getAllByText(/login/i);
      expect(loginElements.length).toBeGreaterThanOrEqual(1);
    });
  });
});

