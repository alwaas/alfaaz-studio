"use client";

import { useEffect, useState } from "react";
import { Cpu, Zap } from "lucide-react";
import { api } from "@/services/api";
import { SystemDeviceTelemetry } from "@/types";

export function HardwareBadge() {
  const [telemetry, setTelemetry] = useState<SystemDeviceTelemetry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function fetchTelemetry() {
      try {
        const data = await api.getDeviceTelemetry();
        if (mounted) {
          setTelemetry(data);
          setLoading(false);
        }
      } catch {
        if (mounted) {
          // Fallback if backend is offline
          setTelemetry({
            device: "cpu",
            cpu_count: 4,
            cpu_percent: 15.0,
            ram_total_mb: 16384,
            ram_available_mb: 8192,
            cuda_available: false,
          });
          setLoading(false);
        }
      }
    }

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (loading || !telemetry) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-studio-card border border-studio-border text-xs text-studio-muted animate-pulse">
        <span className="w-2 h-2 rounded-full bg-studio-muted" />
        Detecting hardware...
      </div>
    );
  }

  const isCuda = telemetry.device === "cuda" || telemetry.cuda_available;

  return (
    <div
      className={`flex items-center gap-2.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
        isCuda
          ? "bg-studio-emerald/10 border-studio-emerald/30 text-studio-emerald"
          : "bg-studio-gold/10 border-studio-gold/30 text-studio-gold"
      }`}
      title={
        isCuda
          ? `NVIDIA CUDA GPU Accelerated (${telemetry.gpu_name || "Active"})`
          : "Running on CPU (Robust fallback mode)"
      }
    >
      <span className="relative flex h-2 w-2">
        <span
          className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
            isCuda ? "bg-studio-emerald" : "bg-studio-gold"
          }`}
        />
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            isCuda ? "bg-studio-emerald" : "bg-studio-gold"
          }`}
        />
      </span>

      {isCuda ? (
        <span className="flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5" />
          <span>CUDA GPU</span>
          {telemetry.vram_free_mb && (
            <span className="text-[10px] opacity-80">
              ({Math.round(telemetry.vram_free_mb / 1024)}GB Free)
            </span>
          )}
        </span>
      ) : (
        <span className="flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5" />
          <span>CPU Mode</span>
          <span className="text-[10px] opacity-80">({telemetry.cpu_count} Cores)</span>
        </span>
      )}
    </div>
  );
}

