"use client";

import { useState } from "react";
import { Mic, Sliders, Upload, CheckCircle2, ShieldAlert } from "lucide-react";

interface VoiceSelectorProps {
  engine: string;
  onChangeEngine: (engine: string) => void;
  speed: number;
  onChangeSpeed: (speed: number) => void;
  pitch: number;
  onChangePitch: (pitch: number) => void;
  speaker: string;
  onChangeSpeaker: (speaker: string) => void;
  referenceFile: File | null;
  onSelectReferenceFile: (file: File | null) => void;
}

const TTS_ENGINES = [
  {
    id: "f5-tts",
    name: "F5-TTS",
    description: "Flow Matching zero-shot voice cloning with reference audio",
    sampleRate: "24,000 Hz",
    license: "CC-BY-NC-4.0 (Personal Use)",
    supportsCloning: true,
  },
  {
    id: "melotts",
    name: "MeloTTS",
    description: "Fast multi-speaker neural speech with emotional expression",
    sampleRate: "22,050 Hz",
    license: "MIT (Commercial Friendly)",
    supportsCloning: false,
  },
  {
    id: "piper",
    name: "Piper TTS",
    description: "Ultra-fast CPU-optimized on-device synthesis engine",
    sampleRate: "22,050 Hz",
    license: "MIT (Commercial Friendly)",
    supportsCloning: false,
  },
];

const MELO_SPEAKERS = [
  { id: "ur-poet-male", name: "Poet Baritone (مردانہ شاعرانہ لہجہ)" },
  { id: "ur-poet-female", name: "Poet Melodic (نسوانی نغمگی)" },
  { id: "ur-default", name: "Standard Urdu (معیاری اردو)" },
];

export function VoiceSelector({
  engine,
  onChangeEngine,
  speed,
  onChangeSpeed,
  pitch,
  onChangePitch,
  speaker,
  onChangeSpeaker,
  referenceFile,
  onSelectReferenceFile,
}: VoiceSelectorProps) {
  const [dragActive, setDragActive] = useState(false);

  const selectedEngineObj = TTS_ENGINES.find((e) => e.id === engine) || TTS_ENGINES[0];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("audio/") || file.name.endsWith(".wav") || file.name.endsWith(".mp3")) {
        onSelectReferenceFile(file);
      }
    }
  };

  return (
    <div className="bg-studio-card border border-studio-border rounded-2xl p-6 shadow-studio">
      <div className="flex items-center gap-2.5 pb-5 border-b border-studio-border">
        <Mic className="w-5 h-5 text-studio-gold" />
        <h2 className="text-base font-semibold text-studio-text">
          Voice Synthesis Engine
        </h2>
        <span className="font-nastaliq text-studio-muted text-sm pr-1">
          (صوتی انجن)
        </span>
      </div>

      {/* Engine Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 my-5">
        {TTS_ENGINES.map((item) => {
          const isSelected = engine === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onChangeEngine(item.id)}
              className={`p-4 rounded-xl text-left border transition-all ${
                isSelected
                  ? "bg-studio-gold/10 border-studio-gold shadow-gold"
                  : "bg-studio-surface border-studio-border hover:border-studio-borderLight"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-sm text-studio-text">{item.name}</span>
                {isSelected && <CheckCircle2 className="w-4 h-4 text-studio-gold" />}
              </div>
              <p className="text-xs text-studio-muted line-clamp-2 mb-3">
                {item.description}
              </p>
              <div className="flex items-center justify-between text-[11px] text-studio-muted border-t border-studio-border/60 pt-2">
                <span>{item.sampleRate}</span>
                <span className="text-[10px] opacity-75">{item.license.split(" ")[0]}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* F5-TTS License Notice */}
      {engine === "f5-tts" && (
        <div className="mb-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-2.5 text-xs text-amber-300">
          <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <strong>Personal Use License:</strong> F5-TTS operates under CC-BY-NC-4.0. Reels generated with this engine are strictly for non-commercial personal enjoyment.
          </div>
        </div>
      )}

      {/* Voice Cloning Reference File Upload (F5-TTS) */}
      {selectedEngineObj.supportsCloning && (
        <div className="mb-5 p-4 rounded-xl bg-studio-surface border border-studio-border">
          <label className="block text-xs font-semibold text-studio-text mb-1">
            Reference Audio for Voice Cloning (آواز کی نقل)
          </label>
          <p className="text-[11px] text-studio-muted mb-3">
            Upload 3 to 15 seconds of clean poetry recitation or speech sample (.wav / .mp3).
          </p>

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-5 text-center transition-colors ${
              dragActive
                ? "border-studio-gold bg-studio-gold/5"
                : "border-studio-border hover:border-studio-gold/40"
            }`}
          >
            {referenceFile ? (
              <div className="flex items-center justify-between gap-3 px-3 py-2 bg-studio-card rounded-lg border border-studio-border">
                <span className="text-xs text-studio-text font-medium truncate">
                  🎵 {referenceFile.name} ({(referenceFile.size / 1024).toFixed(0)} KB)
                </span>
                <button
                  type="button"
                  onClick={() => onSelectReferenceFile(null)}
                  className="text-xs text-studio-rose hover:underline"
                >
                  Remove
                </button>
              </div>
            ) : (
              <div>
                <Upload className="w-6 h-6 text-studio-muted mx-auto mb-2" />
                <label className="cursor-pointer text-xs font-medium text-studio-gold hover:underline">
                  <span>Browse audio file</span>
                  <input
                    type="file"
                    accept="audio/*,.wav,.mp3"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        onSelectReferenceFile(e.target.files[0]);
                      }
                    }}
                  />
                </label>
                <p className="text-[10px] text-studio-muted mt-1">or drag & drop audio here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Speaker Preset (MeloTTS) */}
      {engine === "melotts" && (
        <div className="mb-5 p-4 rounded-xl bg-studio-surface border border-studio-border">
          <label className="block text-xs font-semibold text-studio-text mb-2">
            Urdu Speaker Voice (لہجہ)
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {MELO_SPEAKERS.map((spk) => (
              <button
                key={spk.id}
                type="button"
                onClick={() => onChangeSpeaker(spk.id)}
                className={`px-3 py-2 text-xs rounded-lg border text-left transition-colors font-nastaliq ${
                  speaker === spk.id
                    ? "bg-studio-gold/20 border-studio-gold text-studio-gold"
                    : "bg-studio-card border-studio-border text-studio-text hover:border-studio-borderLight"
                }`}
              >
                {spk.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Synthesis Tuning: Speed & Pitch */}
      <div className="pt-4 border-t border-studio-border grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-studio-muted flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5" />
              Recitation Speed (رفتار)
            </span>
            <span className="text-xs font-mono font-semibold text-studio-gold">
              {speed.toFixed(2)}x
            </span>
          </div>
          <input
            type="range"
            min="0.5"
            max="1.8"
            step="0.05"
            value={speed}
            onChange={(e) => onChangeSpeed(parseFloat(e.target.value))}
            className="w-full accent-studio-gold cursor-pointer"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-studio-muted flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5" />
              Pitch Tuning (سر)
            </span>
            <span className="text-xs font-mono font-semibold text-studio-gold">
              {pitch > 0 ? `+${pitch.toFixed(1)}` : pitch.toFixed(1)}
            </span>
          </div>
          <input
            type="range"
            min="-1.0"
            max="1.0"
            step="0.1"
            value={pitch}
            onChange={(e) => onChangePitch(parseFloat(e.target.value))}
            className="w-full accent-studio-gold cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}

