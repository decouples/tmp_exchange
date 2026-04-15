import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "GenReader",
  description: "AI-driven PDF & image text localization",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-[var(--border)]">
          <nav className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
            <Link href="/" className="text-lg font-semibold tracking-tight">
              GenReader
            </Link>
            <div className="flex items-center gap-6 text-sm">
              <Link href="/upload" className="hover:text-white/90">Upload</Link>
              <Link href="/tasks" className="hover:text-white/90">Tasks</Link>
              <Link href="/login" className="hover:text-white/90">Login</Link>
            </div>
          </nav>
        </header>
        <main className="max-w-6xl mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
