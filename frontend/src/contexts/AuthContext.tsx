import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/apiClient';
import { clearFarmState } from '../utils/storage';

export type UserRole = 'farmer' | 'buyer';

export interface User {
  id: number;
  username: string;
  email?: string;
  role?: UserRole | string;
  farmer_id?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  activeRole: UserRole;
  setRole: (role: UserRole) => void;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem('user') || localStorage.getItem('cropshift_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [activeRoleState, setActiveRoleState] = useState<UserRole>(() => {
    const storedRole = localStorage.getItem('cropshift_active_role') || localStorage.getItem('cropshift_role');
    return storedRole && storedRole.toLowerCase() === 'buyer' ? 'buyer' : 'farmer';
  });

  // Authoritative activeRole derived strictly from authenticated user profile or stored client state
  const rawRole = user?.role || localStorage.getItem('cropshift_role') || localStorage.getItem('cropshift_active_role');
  const activeRole: UserRole = rawRole
    ? (rawRole.toLowerCase() as UserRole)
    : activeRoleState;

  const setRole = (role: UserRole) => {
    // If logged in with profile role, keep activeRole aligned
    if (user?.role) {
      const authRole = (user.role as string).toLowerCase() as UserRole;
      setActiveRoleState(authRole);
      localStorage.setItem('cropshift_active_role', authRole);
      return;
    }
    setActiveRoleState(role);
    localStorage.setItem('cropshift_active_role', role);
    localStorage.setItem('cropshift_role', role);
  };

  useEffect(() => {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    const authRole = newUser.role
      ? (newUser.role as string).toLowerCase() as UserRole
      : 'farmer';
    setActiveRoleState(authRole);
    localStorage.setItem('cropshift_active_role', authRole);
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify({ ...newUser, role: authRole.toUpperCase() }));
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  };

  const logout = () => {
    clearFarmState();
    setToken(null);
    setUser(null);
    setActiveRoleState('farmer');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('cropshift_user');
    localStorage.removeItem('cropshift_active_role');
    localStorage.removeItem('cropshift_role');
    delete apiClient.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, activeRole, setRole, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
