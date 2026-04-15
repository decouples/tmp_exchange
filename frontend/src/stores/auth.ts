"use client";

import { create } from "zustand";

import { api, tokenStore } from "@/lib/api";
import type { UserRead } from "@/types";

type AuthState = {
  user: UserRead | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hydrate: () => Promise<void>;
};

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: false,
  async login(email, password) {
    set({ loading: true });
    try {
      const res = await api.login(email, password);
      tokenStore.set(res.access_token);
      set({ user: res.user });
    } finally {
      set({ loading: false });
    }
  },
  logout() {
    tokenStore.clear();
    set({ user: null });
  },
  async hydrate() {
    if (!tokenStore.get()) return;
    try {
      const me = await api.me();
      set({ user: me });
    } catch {
      tokenStore.clear();
      set({ user: null });
    }
  },
}));
