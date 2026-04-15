"use client";

import { tokenStore } from "./api";

export type ProgressEvent = {
  task_id: string;
  status: string;
  progress: number;
  message?: string;
};

const WS_BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_WS_BASE_URL) ||
  "ws://localhost:8000";

export function subscribeTask(
  taskId: string,
  onEvent: (e: ProgressEvent) => void,
  onClose?: () => void,
): () => void {
  const token = tokenStore.get();
  const url = `${WS_BASE}/api/v1/ws/tasks/${taskId}?token=${encodeURIComponent(token || "")}`;
  let closed = false;
  let ws: WebSocket | null = null;

  const open = () => {
    ws = new WebSocket(url);
    ws.onmessage = (e) => {
      try {
        onEvent(JSON.parse(e.data));
      } catch {
        /* ignore */
      }
    };
    ws.onclose = () => {
      if (!closed) onClose?.();
    };
  };
  open();

  return () => {
    closed = true;
    ws?.close();
  };
}
