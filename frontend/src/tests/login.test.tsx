import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import LoginPage from '../pages/LoginPage';
import { AuthProvider } from '../contexts/AuthContext';
import apiClient from '../services/apiClient';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../services/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    defaults: { headers: { common: {} } },
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

const renderLoginPage = () =>
  render(
    <BrowserRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </BrowserRouter>
  );

describe('LoginPage Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders standalone login page with Farmer and Buyer portal cards and auth tabs', () => {
    renderLoginPage();

    expect(screen.getByText('Choose your portal')).toBeInTheDocument();
    expect(screen.getAllByText('Farmer Portal').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Buyer Portal').length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /🔑 Sign In/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /✨ Sign Up/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByTestId('login-submit-btn')).toBeInTheDocument();
    expect(screen.getByText(/Demo Farmer Credentials:/i)).toBeInTheDocument();
  });

  it('switches between Farmer and Buyer portal cards and updates demo credentials', () => {
    renderLoginPage();

    const buyerCard = screen.getByRole('button', { name: /buyer portal/i });
    fireEvent.click(buyerCard);

    expect(screen.getByText(/Demo Buyer Credentials:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toHaveValue('buyer_demo');

    const fillBtn = screen.getByRole('button', { name: /fill credentials/i });
    fireEvent.click(fillBtn);

    expect(screen.getByLabelText(/username/i)).toHaveValue('buyer_demo');
    expect(screen.getByLabelText(/password/i)).toHaveValue('password123');
  });

  it('submits farmer credentials and navigates to farmer home on success', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { access_token: 'fake_jwt_token', token_type: 'bearer' },
    });
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { id: 1, username: 'demo', email: 'demo@cropshift.com', role: 'FARMER' },
    });

    renderLoginPage();

    fireEvent.click(screen.getByTestId('login-submit-btn'));

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/auth/token',
        expect.any(URLSearchParams),
        expect.any(Object)
      );
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    expect(localStorage.getItem('token')).toBe('fake_jwt_token');
  });

  it('submits buyer credentials and navigates to buyer portal on success', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { access_token: 'buyer_jwt_token', token_type: 'bearer' },
    });
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { id: 2, username: 'buyer_demo', email: 'buyer@cropshift.com', role: 'BUYER' },
    });

    renderLoginPage();

    // Select Buyer card
    const buyerCard = screen.getByRole('button', { name: /buyer portal/i });
    fireEvent.click(buyerCard);

    fireEvent.click(screen.getByTestId('login-submit-btn'));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/buyer');
    });

    expect(localStorage.getItem('token')).toBe('buyer_jwt_token');
  });

  it('supports Sign Up registration for new users', async () => {
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({ data: { id: 10, username: 'newfarmer', email: 'newfarmer@cropshift.com', role: 'FARMER' } })
      .mockResolvedValueOnce({ data: { access_token: 'new_token', token_type: 'bearer' } });
    
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { id: 10, username: 'newfarmer', email: 'newfarmer@cropshift.com', role: 'FARMER' },
    });

    renderLoginPage();

    // Switch to Sign Up tab
    const signUpTab = screen.getByRole('button', { name: /✨ Sign Up/i });
    fireEvent.click(signUpTab);

    expect(screen.getByText(/Create New Farmer Account/i)).toBeInTheDocument();

    const usernameInput = screen.getByLabelText(/choose username/i);
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/choose password/i);

    fireEvent.change(usernameInput, { target: { value: 'newfarmer' } });
    fireEvent.change(emailInput, { target: { value: 'newfarmer@cropshift.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    const submitBtn = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/auth/register', {
        username: 'newfarmer',
        email: 'newfarmer@cropshift.com',
        password: 'password123',
        role: 'FARMER',
      });
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('displays error message when login fails', async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce({
      response: { data: { detail: 'Incorrect username or password' } },
      message: 'Incorrect username or password',
    });
    renderLoginPage();
    const usernameInput = screen.getByPlaceholderText(/Enter your username/i);
    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);
    fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    
    await waitFor(() => {
      expect(usernameInput).toHaveValue('wronguser');
    });

    fireEvent.click(screen.getByTestId('login-submit-btn'));

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent(/Incorrect username or password/i);
  });
});
