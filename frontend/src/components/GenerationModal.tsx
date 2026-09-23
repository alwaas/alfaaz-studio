"use client";

import { useEffect, useRef } from "react";
import { Loader2, CheckCircle2, XCircle, Terminal, X } from "lucide-react";
import { Job } from "@/types";

interface GenerationModalProps {
  isOpen: boolean;
  job: Job | null;
  logs: string[];
  onCancel: () => void;
  onClose: () => void;
}

export function GenerationModal({
  isOpen,
  job,
  logs,
  onCancel,
  onClose,
}: GenerationModalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  if (!isOpen || !job) return null;

  const isCompleted = job.status === "completed";
  const isFailed = job.status === "failed";
  const isCancelled = job.status === "cancelled";
  const isProcessing = job.status === "processing" || job.status === "pending";

  const getStepStatus = (minProgress: number) => {
    if (isFailed) return "failed";
    if (job.progress >= minProgress) return "done";
    if (job.progress >= minProgress - 25) return "active";
    return "pending";
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div className="relative w-full max-w-xl rounded-2xl bg-studio-card border border-studio-border p-6 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-studio-border">
          <div className="flex items-center gap-2.5">
            {isProcessing && <Loader2 className="w-5 h-5 text-studio-gold animate-spin" />}
            {isCompleted && <CheckCircle2 className="w-5 h-5 text-studio-emerald" />}
            {isFailed && <XCircle className="w-5 h-5 text-studio-rose" />}
            <h3 className="text-base font-semibold text-studio-text">
              {isCompleted
                ? "Audio Synthesized Successfully!"
                : isFailed
                ? "Synthesis Failed"
                : "Synthesizing Urdu Poetry Voiceover"}
            </h3>
          </div>

          {(isCompleted || isFailed || isCancelled) && (
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-studio-muted hover:text-studio-text hover:bg-studio-hover"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Progress Bar */}
        <div className="my-5">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-studio-muted">
              {job.status === "processing" ? "Processing neural audio pipeline..." : job.status}
            </span>
            <span className="font-mono font-bold text-studio-gold">
              {job.progress.toFixed(0)}%
            </span>
          </div>

          <div className="w-full h-2 rounded-full bg-studio-surface overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                isCompleted
                  ? "bg-studio-emerald"
                  : isFailed
                  ? "bg-studio-rose"
                  : "bg-gradient-to-r from-studio-amber to-studio-gold"
              }`}
              style={{ width: `${Math.max(5, job.progress)}%` }}
            />
          </div>
        </div>

        {/* Pipeline Steps Indicator */}
        <div className="grid grid-cols-3 gap-2 my-4 text-center text-xs">
          <div
            className={`p-2 rounded-xl border ${
              getStepStatus(25) === "done"
                ? "bg-studio-emerald/10 border-studio-emerald/40 text-studio-emerald"
                : getStepStatus(25) === "active"
                ? "bg-studio-gold/10 border-studio-gold text-studio-gold font-medium"
                : "bg-studio-surface border-studio-border text-studio-muted"
            }`}
          >
            1. Urdu Text Cleaning
          </div>

          <div
            className={`p-2 rounded-xl border ${
              getStepStatus(75) === "done"
                ? "bg-studio-emerald/10 border-studio-emerald/40 text-studio-emerald"
                : getStepStatus(75) === "active"
                ? "bg-studio-gold/10 border-studio-gold text-studio-gold font-medium"
                : "bg-studio-surface border-studio-border text-studio-muted"
            }`}
          >
            2. Neural TTS Synthesis
          </div>

          <div
            className={`p-2 rounded-xl border ${
              getStepStatus(100) === "done"
                ? "bg-studio-emerald/10 border-studio-emerald/40 text-studio-emerald"
                : getStepStatus(100) === "active"
                ? "bg-studio-gold/10 border-studio-gold text-studio-gold font-medium"
                : "bg-studio-surface border-studio-border text-studio-muted"
            }`}
          >
            3. DSP Audio Mastering
          </div>
        </div>

        {/* Real-time Logs Terminal */}
        <div className="rounded-xl bg-black/60 border border-studio-border/70 p-3 my-4">
          <div className="flex items-center gap-2 pb-2 mb-2 border-b border-white/10 text-[11px] text-studio-muted">
            <Terminal className="w-3.5 h-3.5 text-studio-gold" />
            <span>Worker Execution Logs (ریئل ٹائم لاگز)</span>
          </div>

          <div
            ref={terminalRef}
            className="h-28 overflow-y-auto font-mono text-[11px] text-studio-muted space-y-1 pr-1"
          >
            {logs.length === 0 ? (
              <span className="opacity-50 italic">Connecting to background task runner...</span>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="leading-tight">
                  <span className="text-studio-gold/70">›</span> {log}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-studio-border">
          {isProcessing && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-xs font-semibold rounded-xl bg-studio-surface hover:bg-studio-rose/20 text-studio-muted hover:text-studio-rose border border-studio-border transition-colors"
            >
              Cancel Synthesis
            </button>
          )}

          {isCompleted && (
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2 text-xs font-semibold rounded-xl bg-studio-emerald hover:bg-studio-emerald/90 text-studio-bg transition-colors"
            >
              Open Audio in Editor
            </button>
          )}

          {isFailed && (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold rounded-xl bg-studio-surface hover:bg-studio-hover text-studio-text border border-studio-border transition-colors"
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

