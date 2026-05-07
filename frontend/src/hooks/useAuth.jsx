import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("emotion_token")));

  useEffect(() => {
    const token = localStorage.getItem("emotion_token");
    if (!token) return;
    authApi
      .me()
      .then(({ data }) => setUser(data))
      .catch(() => localStorage.removeItem("emotion_token"))
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      async login(payload) {
        const { data } = await authApi.login(payload);
        localStorage.setItem("emotion_token", data.access_token);
        setUser(data.user);
      },
      async register(payload) {
        const { data } = await authApi.register(payload);
        localStorage.setItem("emotion_token", data.access_token);
        setUser(data.user);
      },
      logout() {
        localStorage.removeItem("emotion_token");
        setUser(null);
      },
      setUser
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
