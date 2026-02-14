"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "./api";
import type { UserInfo } from "./types";

interface AuthState {
  user: UserInfo | null;
  loading: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = api.getToken();
    if (token) {
      api
        .get<UserInfo>("/api/v1/auth/me")
        .then(setUser)
        .catch(() => {
          api.setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string, rememberMe = false) => {
    const data = await api.post<{
      access_token: string;
      user_email: string;
      user_name: string;
    }>("/api/v1/auth/login", { email, password, remember_me: rememberMe });
    api.setToken(data.access_token);
    const userInfo = await api.get<UserInfo>("/api/v1/auth/me");
    setUser(userInfo);
  };

  const logout = async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } finally {
      api.setToken(null);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
