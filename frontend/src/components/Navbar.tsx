"use client";

import Link from "next/link";
import { Sparkles, Mic2 } from "lucide-react";
import { HardwareBadge } from "./HardwareBadge";

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-studio-border bg-studio-bg/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-studio-gold to-studio-amber flex items-center justify-center shadow-gold">
            <Mic2 className="w-5 h-5 text-studio-bg font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-studio-text">
                AlfaazStudio
              </span>
              <span className="font-nastaliq text-studio-gold text-lg font-bold">
                الفاظ اسٹوڈیو
              </span>
            </div>
            <p className="text-[10px] text-studio-muted tracking-wider uppercase font-semibold">
              Urdu Poetry AI Voice-over Studio
            </p>
          </div>
        </div>

        {/* Center / Hardware Telemetry */}
        <div className="flex items-center gap-4">
          <HardwareBadge />
          
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-studio-surface border border-studio-border text-xs text-studio-muted">
            <Sparkles className="w-3.5 h-3.5 text-studio-gold" />
            <span>9:16 Reels Engine</span>
          </div>
        </div>
      </div>
    </header>
  );
}

