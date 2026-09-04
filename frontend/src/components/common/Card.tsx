import React from 'react';

interface CardProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  headerTag?: 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export default function Card({
  title,
  subtitle,
  children,
  footer,
  className = '',
  headerTag = 'h3',
  ...props
}: CardProps & React.HTMLAttributes<HTMLDivElement>) {
  const HeaderComponent = headerTag;
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`} {...props}>
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {title && <HeaderComponent className="text-lg font-bold text-gray-900 leading-tight">{title}</HeaderComponent>}
          {subtitle && <p className="mt-1 text-sm text-gray-500 leading-snug">{subtitle}</p>}
        </div>
      )}
      <div className="px-6 py-4">
        {children}
      </div>
      {footer && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
}
