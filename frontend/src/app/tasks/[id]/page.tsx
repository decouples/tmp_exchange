"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { DocumentViewer } from "@/components/viewer/DocumentViewer";
import { api } from "@/lib/api";
import { subscribeTask, type ProgressEvent } from "@/lib/ws";
import { useAuth } from "@/stores/auth";
import type { OCRTask } from "@/types";

export default function TaskDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const [taskId, setTaskId] = useState<string | null>(null);
  useEffect(() => {
    void params.then((p) => setTaskId(p.id));
  }, [params]);

  const hydrate = useAuth((s) => s.hydrate);
  const user = useAuth((s) => s.user);
  const [task, setTask] = useState<OCRTask | null>(null);
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (!taskId || !user) return;
    let cancelled = false;

    async function load() {
      try {
        const t = await api.getTask(taskId!);
        if (!cancelled) setTask(t);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      }
    }
    void load();

    const unsub = subscribeTask(
      taskId,
      (e) => {
        setProgress(e);
        if (["SUCCESS", "FAILED", "CANCELLED"].includes(e.status)) void load();
      },
      () => {
        /* closed */
      },
    );
    const poll = setInterval(load, 4000);
    return () => {
      cancelled = true;
      unsub();
      clearInterval(poll);
    };
  }, [taskId, user]);

  if (!user) {
    return (
      <div className="card p-6">
        <p className="text-white/70">
          Please <a className="text-indigo-300 underline" href="/login">sign in</a>.
        </p>
      </div>
    );
  }

  if (error) return <div className="text-red-400">{error}</div>;
  if (!task) return <div className="text-white/50">Loading…</div>;

  const matches = task.result?.matches ?? [];
  const live = progress ?? { status: task.status, progress: task.progress, task_id: task.task_id };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-white/50">{task.task_id}</div>
          <h1 className="text-2xl font-semibold">Query: {task.query}</h1>
        </div>
        {["PENDING", "QUEUED", "PROCESSING"].includes(live.status) && (
          <Button
            variant="danger"
            onClick={async () => {
              const t = await api.cancelTask(task.task_id);
              setTask(t);
            }}
          >
            Cancel
          </Button>
        )}
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-white/70">Status: {live.status}</span>
          <span className="text-white/50">{live.progress}%</span>
        </div>
        <div className="h-2 rounded-full bg-white/10 overflow-hidden">
          <div className="h-full bg-indigo-500" style={{ width: `${live.progress}%` }} />
        </div>
        {progress?.message && (
          <div className="mt-2 text-xs text-white/50">{progress.message}</div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-4">
          <h2 className="text-sm text-white/60 mb-3">Document</h2>
          <DocumentViewer fileId={task.file_id} matches={matches} />
        </div>
        <div className="card p-4 overflow-auto max-h-[70vh]">
          <h2 className="text-sm text-white/60 mb-3">
            Matches ({matches.length}) · engine: {task.result?.engine ?? "—"}
          </h2>
          <ol className="space-y-2 text-sm">
            {matches.map((m, i) => (
              <li key={i} className="border border-[var(--border)] rounded-md p-2">
                <div className="font-medium">{m.text}</div>
                <div className="text-xs text-white/50">
                  page {m.bbox.page} · x={m.bbox.x.toFixed(3)} y={m.bbox.y.toFixed(3)} w=
                  {m.bbox.w.toFixed(3)} h={m.bbox.h.toFixed(3)} · conf{" "}
                  {m.confidence.toFixed(2)}
                </div>
              </li>
            ))}
            {matches.length === 0 && task.status === "SUCCESS" && (
              <li className="text-white/50">No matches found.</li>
            )}
          </ol>
          {task.error && (
            <div className="mt-3 text-red-400 text-xs whitespace-pre-wrap">{task.error}</div>
          )}
          {task.result && (
            <button
              className="mt-4 text-xs text-indigo-300 underline"
              onClick={() => {
                const blob = new Blob([JSON.stringify(task.result, null, 2)], {
                  type: "application/json",
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${task.task_id}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              Export JSON
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
