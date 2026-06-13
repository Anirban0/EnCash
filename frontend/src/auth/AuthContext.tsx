import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, tokenStore } from "../api/client";

interface AuthState {
  email: string | null;
  authenticated: boolean;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState>(null as never);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (tokenStore.access) {
      api
        .get("/auth/me/")
        .then((r) => setEmail(r.data.email))
        .catch(() => tokenStore.clear())
        .finally(() => setReady(true));
    } else {
      setReady(true);
    }
  }, []);

  async function login(emailArg: string, password: string) {
    const { data } = await api.post("/auth/token/", { email: emailArg, password });
    tokenStore.set(data.access, data.refresh);
    const me = await api.get("/auth/me/");
    setEmail(me.data.email);
  }

  async function register(emailArg: string, password: string) {
    await api.post("/auth/register/", { email: emailArg, password });
    await login(emailArg, password);
  }

  async function logout() {
    try {
      if (tokenStore.refresh) await api.post("/auth/logout/", { refresh: tokenStore.refresh });
    } finally {
      tokenStore.clear();
      setEmail(null);
    }
  }

  return (
    <AuthContext.Provider
      value={{ email, authenticated: !!email, ready, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
