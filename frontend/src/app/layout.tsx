import type { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "AlfaazStudio | الفاظ اسٹوڈیو - Urdu Poetry AI Voice-over Studio",
  description:
    "Open-source local neural speech synthesis and 9:16 Instagram Reel generator for Urdu poetry.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ur" dir="ltr" className="dark">
      <body className="min-h-screen flex flex-col bg-studio-bg text-studio-text antialiased">
        <Navbar />
        <main className="flex-1 pb-16">{children}</main>
        <footer className="py-6 border-t border-studio-border bg-studio-surface/50 text-center text-xs text-studio-muted">
          <div className="max-w-7xl mx-auto px-4">
            <p>
              AlfaazStudio (الفاظ اسٹوڈیو) • Local-first Urdu Neural TTS Studio • Zero Cloud API Dependency
            </p>
            <p className="mt-1 text-[11px] opacity-75">
              F5-TTS model licensed under CC-BY-NC-4.0 (Personal Use Only). MeloTTS & Piper under MIT.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}

