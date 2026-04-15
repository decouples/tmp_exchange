"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/stores/auth";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuth((s) => s.login);
  const loading = useAuth((s) => s.loading);
  const [email, setEmail] = useState("demo@genreader.local");
  const [password, setPassword] = useState("demo");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      router.push("/upload");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <div className="max-w-sm mx-auto card p-8">
      <h1 className="text-2xl font-semibold mb-6">Sign in</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-xs text-white/60 block mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full h-10 px-3 rounded-md bg-white/5 border border-[var(--border)] focus:outline-none focus:border-indigo-400"
          />
        </div>
        <div>
          <label className="text-xs text-white/60 block mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full h-10 px-3 rounded-md bg-white/5 border border-[var(--border)] focus:outline-none focus:border-indigo-400"
          />
        </div>
        {error && <div className="text-red-400 text-sm">{error}</div>}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </Button>
        <p className="text-xs text-white/50">
          Demo credentials: <code>demo@genreader.local</code> / <code>demo</code>
        </p>
      </form>
    </div>
  );
}
