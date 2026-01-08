import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from './api';
import type { User } from './types';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshUser = async () => {
        if (apiClient.getToken()) {
            try {
                const result = await apiClient.getCurrentUser();
                if (result.code === 0 && result.data) {
                    setUser(result.data);
                } else {
                    setUser(null);
                    apiClient.clearToken();
                }
            } catch (error) {
                console.error('Failed to fetch user:', error);
                setUser(null);
                apiClient.clearToken();
            }
        }
        setLoading(false);
    };

    useEffect(() => {
        refreshUser();
    }, []);

    const login = async (username: string, password: string) => {
        await apiClient.login({ username, password });
        await refreshUser();
    };

    const logout = () => {
        apiClient.clearToken();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
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
