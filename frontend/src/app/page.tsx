import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">
          Find text in documents — with pixel-perfect coordinates.
        </h1>
        <p className="max-w-2xl text-white/70 text-lg">
          GenReader uses a local vision-language model (Qwen-VL) to locate any
          query text inside PDFs and images, then renders the result with
          highlight boxes. Async queue, multi-user, Docker-ready.
        </p>
        <div className="flex gap-3">
          <Link href="/upload">
            <Button size="lg">Start uploading</Button>
          </Link>
          <Link href="/tasks">
            <Button size="lg" variant="secondary">View tasks</Button>
          </Link>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {[
          { t: "VLM-first", d: "Qwen-VL understands document layout, not just characters." },
          { t: "Async queue", d: "Redis + arq. Scale workers horizontally." },
          { t: "Live progress", d: "WebSocket streams status while your task runs." },
        ].map((f) => (
          <div key={f.t} className="card p-5">
            <div className="text-sm text-indigo-300/90 font-medium">{f.t}</div>
            <div className="mt-2 text-white/70 text-sm">{f.d}</div>
          </div>
        ))}
      </section>
    </div>
  );
}
