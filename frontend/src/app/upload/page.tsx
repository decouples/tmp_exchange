"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useAuth } from "@/stores/auth";

export default function UploadPage() {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const hydrate = useAuth((s) => s.hydrate);

  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState("");
  const [priority, setPriority] = useState("default");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!file || !query) {
      setError("Pick a file and enter a query");
      return;
    }
    setBusy(true);
    try {
      const res = await api.uploadAndSubmit(file, query, priority);
      router.push(`/tasks/${res.task_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  if (!user) {
    return (
      <div className="card p-6">
        <p className="text-white/70">
          Please <a className="text-indigo-300 underline" href="/login">sign in</a> to upload.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-semibold">Upload a document</h1>

      <form onSubmit={onSubmit} className="card p-6 space-y-5">
        <div>
          <label className="text-xs text-white/60 block mb-2">File (PDF / PNG / JPG)</label>
          <input
            type="file"
            accept="application/pdf,image/png,image/jpeg,image/webp"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-white/80 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-indigo-500 file:text-white hover:file:bg-indigo-600 file:cursor-pointer"
          />
          {file && (
            <div className="text-xs text-white/50 mt-1">
              {file.name} · {(file.size / 1024).toFixed(1)} KB
            </div>
          )}
        </div>

        <div>
          <label className="text-xs text-white/60 block mb-2">
            What to find (keyword or natural-language description)
          </label>
          <textarea
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. invoice total, customer address, signatures…"
            className="w-full p-3 rounded-md bg-white/5 border border-[var(--border)] focus:outline-none focus:border-indigo-400"
          />
        </div>

        <div>
          <label className="text-xs text-white/60 block mb-2">Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="h-10 px-3 rounded-md bg-white/5 border border-[var(--border)]"
          >
            <option value="high">high</option>
            <option value="default">default</option>
            <option value="batch">batch</option>
          </select>
        </div>

        {error && <div className="text-red-400 text-sm">{error}</div>}

        <Button type="submit" disabled={busy} size="lg">
          {busy ? "Submitting…" : "Submit OCR task"}
        </Button>
      </form>
    </div>
  );
}
