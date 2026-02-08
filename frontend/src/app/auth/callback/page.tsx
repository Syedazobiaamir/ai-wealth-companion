'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    const provider = searchParams.get('provider');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setError(errorParam);
      return;
    }

    if (accessToken) {
      // Store the token
      localStorage.setItem('accessToken', accessToken);

      // Fetch user info and store it
      const fetchUser = async () => {
        try {
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
          });

          if (response.ok) {
            const data = await response.json();
            const userData = data.data || data;
            localStorage.setItem('user', JSON.stringify(userData));
          }

          // Redirect to dashboard
          window.location.href = '/dashboard';
        } catch (err) {
          console.error('Failed to fetch user:', err);
          // Still redirect, user can re-authenticate if needed
          window.location.href = '/dashboard';
        }
      };

      fetchUser();
    } else {
      setError('No access token received');
    }
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-purple-50/50 to-blue-50/50 dark:from-gray-950 dark:via-purple-950/20 dark:to-blue-950/20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Authentication Error</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
          <a
            href="/login"
            className="px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-purple-600 to-blue-500"
          >
            Return to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-purple-50/50 to-blue-50/50 dark:from-gray-950 dark:via-purple-950/20 dark:to-blue-950/20">
      <div className="text-center">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/25 animate-pulse mx-auto mb-4">
          <span className="text-2xl">💰</span>
        </div>
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
          Completing sign in...
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Please wait while we redirect you.
        </p>
      </div>
    </div>
  );
}
