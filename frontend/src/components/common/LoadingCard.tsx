import React from 'react';
import Card from './Card';

interface LoadingCardProps {
  lines?: number;
  className?: string;
}

export default function LoadingCard({ lines = 3, className = '' }: LoadingCardProps) {
  return (
    <Card className={`animate-pulse ${className}`}>
      {/* Title skeleton */}
      <div className="h-5 bg-gray-200 rounded w-1/3 mb-6"></div>
      
      {/* Body lines skeleton */}
      <div className="space-y-4">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`h-4 bg-gray-200 rounded ${
              index === lines - 1 ? 'w-2/3' : 'w-full'
            }`}
          ></div>
        ))}
      </div>
    </Card>
  );
}
