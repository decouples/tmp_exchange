"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import type { OCRTask } from "@/types";

const STATUS_COLORS: Record<string, string> = {
  PENDING: "bg-white/10 text-white/70",
  QUEUED: "bg-white/10 text-white/70",
  PROCESSING: "bg-indigo-500/20 text-indigo-300",
  SUCCESS: "bg-emerald-500/20 text-emerald-300",
  FAILED: "bg-red-500/20 text-red-300",
  CANCELLED: "bg-yellow-500/20 text-yellow-300",
};

export default function TasksListPage() {
  const hydrate = useAuth((s) => s.hydrate);
  const user = useAuth((s) => s.user);
  const [tasks, setTasks] = useState<OCRTask[]>([]);
  const [filter, setFilter] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    async function load() {
      try {
        const list = await api.listTasks(filter || undefined);
        if (!cancelled) setTasks(list);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      }
    }
    void load();
    const t = setInterval(load, 3000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, [user, filter]);

  if (!user) {
    return (
      <div className="card p-6">
        <p className="text-white/70">
          Please <a className="text-indigo-300 underline" href="/login">sign in</a>.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold">Tasks</h1>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="h-10 px-3 rounded-md bg-white/5 border border-[var(--border)] text-sm"
        >
          <option value="">All</option>
          <option>PENDING</option>
          <option>QUEUED</option>
          <option>PROCESSING</option>
          <option>SUCCESS</option>
          <option>FAILED</option>
          <option>CANCELLED</option>
        </select>
      </div>

      {error && <div className="text-red-400 text-sm">{error}</div>}

      <div className="card divide-y divide-[var(--border)]">
        {tasks.length === 0 && (
          <div className="p-6 text-white/50 text-sm">No tasks yet.</div>
        )}
        {tasks.map((t) => (
          <Link
            key={t.task_id}
            href={`/tasks/${t.task_id}`}
            className="flex items-center justify-between p-4 hover:bg-white/5"
          >
            <div className="min-w-0">
              <div className="font-mono text-xs text-white/50 truncate">{t.task_id}</div>
              <div className="text-sm truncate">{t.query}</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-24 h-2 rounded-full bg-white/10 overflow-hidden">
                <div
                  className="h-full bg-indigo-500"
                  style={{ width: `${t.progress}%` }}
                />
              </div>
              <span
                className={`text-xs px-2 py-1 rounded ${STATUS_COLORS[t.status] ?? "bg-white/10"}`}
              >
                {t.status}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
