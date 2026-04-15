"use client";

import { useEffect, useState } from "react";

import { api, tokenStore } from "@/lib/api";
import type { FileRead, OCRMatch } from "@/types";
import { BBoxOverlay } from "./BBoxOverlay";

type Props = {
  fileId: number;
  matches: OCRMatch[];
};

/** Lightweight viewer: fetches the raw file as a blob (with bearer header),
 *  renders it via an <img> for images, or an <iframe> for PDFs. For images
 *  we overlay bbox highlights; for PDFs the overlay is shown on page 1 of a
 *  PNG preview (rendered server-side by the worker via pdf_service). */
export function DocumentViewer({ fileId, matches }: Props) {
  const [url, setUrl] = useState<string | null>(null);
  const [meta, setMeta] = useState<FileRead | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let revoke: string | null = null;
    async function load() {
      try {
        const files = await api.listFiles();
        const m = files.find((f) => f.id === fileId);
        if (m) setMeta(m);

        const token = tokenStore.get();
        const res = await fetch(api.fileRawUrl(fileId), {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const blob = await res.blob();
        const u = URL.createObjectURL(blob);
        revoke = u;
        setUrl(u);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Load failed");
      }
    }
    void load();
    return () => {
      if (revoke) URL.revokeObjectURL(revoke);
    };
  }, [fileId]);

  if (error) return <div className="text-red-400 text-sm">{error}</div>;
  if (!url || !meta) return <div className="text-white/50 text-sm">Loading…</div>;

  const isImage = meta.content_type.startsWith("image/");
  if (isImage) {
    return (
      <div className="relative inline-block max-w-full">
        <img src={url} alt={meta.filename} className="block max-w-full rounded-md" />
        <BBoxOverlay matches={matches} page={1} />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <iframe
        src={url}
        title={meta.filename}
        className="w-full h-[70vh] rounded-md bg-white"
      />
      <div className="text-xs text-white/50">
        PDFs open inline — bounding-box overlays are available in the JSON
        result below. For in-canvas highlighting use a rendered page preview
        (Phase 8 extension).
      </div>
    </div>
  );
}
