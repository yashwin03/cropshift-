import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  isLoading?: boolean;
}

export default function Button({
  children,
  variant = 'primary',
  isLoading = false,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 touch-target px-5 py-2.5 min-h-[44px]';
  
  const variantStyles = {
    primary: 'bg-primary text-white hover:bg-primary-700 active:bg-primary-800 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed',
    secondary: 'border-2 border-primary text-primary hover:bg-primary-50 active:bg-primary-100 disabled:border-gray-300 disabled:text-gray-400 disabled:cursor-not-allowed',
    ghost: 'text-gray-700 hover:bg-gray-100 active:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed'
  };

  const currentStyles = `${baseStyles} ${variantStyles[variant]} ${className}`;

  return (
    <button
      disabled={disabled || isLoading}
      className={currentStyles}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin -ml-1 mr-3 h-5 w-5 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : null}
      {children}
    </button>
  );
}
