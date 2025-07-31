import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id?: string;
  name: string;
  username: string;
  email: string;
  role: 'user' | 'admin';
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  signup: (userData: {
    name: string;
    username: string;
    email: string;
    password: string;
    role?: 'user' | 'admin';
  }) => Promise<boolean>;
  loading: boolean;
  isAdmin: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const API_BASE = process.env.REACT_APP_API_HTTP || 'http://localhost:8000';

  // 페이지 로드 시 현재 사용자 정보 확인
  useEffect(() => {
    const checkUser = async () => {
      try {
        console.log('Checking current user at:', `${API_BASE}/api/auth/me`);
        const response = await fetch(`${API_BASE}/api/auth/me`, {
          credentials: 'include', // 쿠키 포함
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          console.log('User authenticated:', userData);
        } else {
          console.log('No authenticated user, status:', response.status);
        }
      } catch (error) {
        console.log('Error checking user:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkUser();
  }, [API_BASE]);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      console.log('Attempting login at:', `${API_BASE}/api/auth/login`);
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // 쿠키 포함
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        console.log('Login successful:', data.user);
        return true;
      } else {
        const errorData = await response.json();
        console.error('Login failed:', errorData.detail);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const signup = async (userData: {
    name: string;
    username: string;
    email: string;
    password: string;
    role?: 'user' | 'admin';
  }): Promise<boolean> => {
    try {
      setLoading(true);
      console.log('Attempting signup with data:', { ...userData, password: '[HIDDEN]' });
      const response = await fetch(`${API_BASE}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      console.log('Signup response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Signup successful:', data);
        // 회원가입 성공 후 자동 로그인
        return await login(userData.username, userData.password);
      } else {
        const errorData = await response.json();
        console.error('Signup failed:', errorData);
        
        // 검증 에러 메시지 추출
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map((err: any) => err.msg).join(', ');
          console.error('Validation errors:', errorMessages);
        }
        
        return false;
      }
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const isAdmin = (): boolean => {
    return user?.role === 'admin';
  };

  const value: AuthContextType = {
    user,
    login,
    logout,
    signup,
    loading,
    isAdmin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
