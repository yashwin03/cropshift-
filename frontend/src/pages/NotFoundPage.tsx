import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="p-6 text-center">
      <h1 className="text-3xl font-bold text-danger">404 - Page Not Found</h1>
      <p className="mt-2 text-gray-600 font-medium">The page you are looking for does not exist.</p>
      <Link to="/" className="mt-4 inline-block text-primary font-semibold hover:underline">
        Go Back Home
      </Link>
    </div>
  );
}
