"use client";

import type { FileRead, OCRTask, TokenResponse, UserRead } from "@/types";

const BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_BASE_URL) ||
  "http://localhost:8000";
const PREFIX = "/api/v1";

const TOKEN_KEY = "gr:token";

export const tokenStore = {
  get(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_KEY);
  },
  set(token: string) {
    window.localStorage.setItem(TOKEN_KEY, token);
  },
  clear() {
    window.localStorage.removeItem(TOKEN_KEY);
  },
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = tokenStore.get();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${BASE}${PREFIX}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      detail = body?.error?.message || body?.detail || detail;
    } catch {
      /* noop */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}

export const api = {
  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<UserRead>("/auth/me"),

  listFiles: () => request<FileRead[]>("/files"),
  uploadFile: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<FileRead>("/files", { method: "POST", body: fd });
  },

  submitOcr: (fileId: number, query: string, priority = "default") =>
    request<{ task_id: string; status: string }>("/ocr", {
      method: "POST",
      body: JSON.stringify({ file_id: fileId, query, priority }),
    }),

  uploadAndSubmit: (file: File, query: string, priority = "default") => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("query", query);
    fd.append("priority", priority);
    return request<{ task_id: string; status: string }>("/ocr/upload", {
      method: "POST",
      body: fd,
    });
  },

  listTasks: (status?: string) => {
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";
    return request<OCRTask[]>(`/tasks${qs}`);
  },
  getTask: (taskId: string) => request<OCRTask>(`/tasks/${taskId}`),
  cancelTask: (taskId: string) =>
    request<OCRTask>(`/tasks/${taskId}/cancel`, { method: "POST" }),

  fileRawUrl: (fileId: number) => {
    const token = tokenStore.get();
    return `${BASE}${PREFIX}/files/${fileId}/raw${token ? `?_=${Date.now()}` : ""}`;
  },
};
