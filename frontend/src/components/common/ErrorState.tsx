import React from 'react';
import Button from './Button';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export default function ErrorState({
  title = 'Service Message',
  message,
  onRetry,
  className = ''
}: ErrorStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center bg-red-50 border border-red-200 rounded-xl max-w-lg mx-auto ${className}`} role="alert">
      {/* Warning/Error Icon */}
      <div className="flex items-center justify-center w-12 h-12 text-red-600 bg-red-100 rounded-full mb-4">
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-bold text-red-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6 max-w-sm">{message}</p>
      {onRetry && (
        <Button variant="primary" onClick={onRetry} className="bg-red-700 hover:bg-red-800 text-white">
          Try Again
        </Button>
      )}
    </div>
  );
}
