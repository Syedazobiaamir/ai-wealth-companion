'use client';

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useRef,
  ReactNode,
} from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  display_name?: string;
  preferred_currency: string;
  preferred_locale: string;
  theme_preference?: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<string | null>;
}

interface RegisterData {
  email: string;
  password: string;
  display_name?: string;
  preferred_currency?: string;
  preferred_locale?: string;
}

interface AuthResponse {
  success: boolean;
  data: {
    user: User;
    tokens: {
      access_token: string;
      token_type: string;
      expires_in: number;
    };
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const initRef = useRef(false);
  const router = useRouter();

  const isAuthenticated = !!user && !!accessToken;

  // Fetch current user
  const fetchUser = useCallback(async (token: string): Promise<User | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data.data || data;
    } catch {
      return null;
    }
  }, []);

  // Refresh access token using httpOnly cookie
  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      const newToken = data.data?.access_token || data.access_token;

      if (newToken) {
        setAccessToken(newToken);
        localStorage.setItem('accessToken', newToken);
        return newToken;
      }

      return null;
    } catch {
      return null;
    }
  }, []);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    setMounted(true);

    const initAuth = async () => {
      const storedToken = localStorage.getItem('accessToken');
      const storedUser = localStorage.getItem('user');

      // If we have both stored, use them immediately
      if (storedToken && storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
          setAccessToken(storedToken);
          setIsLoading(false);
          return;
        } catch {
          // Invalid stored user, continue
        }
      }

      // If we have token but no user, fetch user
      if (storedToken) {
        const userData = await fetchUser(storedToken);
        if (userData) {
          setUser(userData);
          setAccessToken(storedToken);
          localStorage.setItem('user', JSON.stringify(userData));
        } else {
          // Token expired, try refresh
          const newToken = await refreshToken();
          if (newToken) {
            const userData = await fetchUser(newToken);
            if (userData) {
              setUser(userData);
              localStorage.setItem('user', JSON.stringify(userData));
            } else {
              localStorage.removeItem('accessToken');
              localStorage.removeItem('user');
            }
          } else {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
          }
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, [fetchUser, refreshToken]);

  // Login
  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || error.error?.message || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    const token = data.data.tokens.access_token;
    const userData = data.data.user;

    // Store in localStorage FIRST
    localStorage.setItem('accessToken', token);
    localStorage.setItem('user', JSON.stringify(userData));

    // Then update state
    setAccessToken(token);
    setUser(userData);
    setIsLoading(false);
  }, []);

  // Register
  const register = useCallback(async (registerData: RegisterData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        email: registerData.email,
        password: registerData.password,
        display_name: registerData.display_name,
        preferred_currency: registerData.preferred_currency || 'PKR',
        preferred_locale: registerData.preferred_locale || 'en',
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || error.error?.message || 'Registration failed');
    }

    const data: AuthResponse = await response.json();
    const token = data.data.tokens.access_token;
    const userData = data.data.user;

    // Store in localStorage FIRST
    localStorage.setItem('accessToken', token);
    localStorage.setItem('user', JSON.stringify(userData));

    // Then update state
    setAccessToken(token);
    setUser(userData);
    setIsLoading(false);
  }, []);

  // Logout
  const logout = useCallback(async () => {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
        credentials: 'include',
      });
    } catch {
      // Ignore errors during logout
    }

    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    setUser(null);
    setAccessToken(null);
    router.push('/login');
  }, [accessToken, router]);

  // Don't render children until mounted to avoid hydration mismatch
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-purple-50/30 to-blue-50/30 dark:from-gray-950 dark:via-purple-950/10 dark:to-blue-950/10">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/25 animate-pulse">
          <span className="text-2xl">💰</span>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshToken,
      }}
    >
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

export { AuthContext };
