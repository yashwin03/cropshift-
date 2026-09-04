import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Card from './Card';
import Button from './Button';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: ('FARMER' | 'BUYER')[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, token } = useAuth();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = (user.role || 'FARMER').toString().toUpperCase() as 'FARMER' | 'BUYER';

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    const targetHome = userRole === 'BUYER' ? '/buyer' : '/';
    return (
      <div className="max-w-md mx-auto py-12 px-4 text-center">
        <Card className="p-6 border-red-200 bg-red-50/50 shadow-md">
          <div className="text-3xl mb-2">🚫</div>
          <h2 className="text-xl font-bold text-red-900">Access Restricted</h2>
          <p className="text-xs text-red-700 mt-2 mb-4">
            Your authenticated account role (<strong>{userRole}</strong>) does not have authorization to view this page.
          </p>
          <Button
            variant="primary"
            onClick={() => (window.location.href = targetHome)}
            className="w-full text-xs py-2.5 font-bold"
          >
            Go to My Authorized Home
          </Button>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
}
