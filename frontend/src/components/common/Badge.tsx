import React from 'react';

interface BadgeProps {
  variant?: 'neutral' | 'success' | 'warning' | 'danger';
  children: React.ReactNode;
  className?: string;
}

export default function Badge({
  variant = 'neutral',
  children,
  className = ''
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold';
  
  const variantStyles = {
    neutral: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800 border border-green-200',
    warning: 'bg-amber-100 text-amber-800 border border-amber-200',
    danger: 'bg-red-100 text-red-800 border border-red-200'
  };

  return (
    <span className={`${baseStyles} ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
}
