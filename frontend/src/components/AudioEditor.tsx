"use client";

import { useEffect, useRef, useState } from "react";
import {
  Play,
  Pause,
  Square,
  Sliders,
  Sparkles,
  Volume2,
  Scissors,
  Download,
  RotateCcw,
  CheckCircle2,
  Music2,
  Layers,
} from "lucide-react";
import { api } from "@/services/api";
import { AudioMasteringRequest, AudioMasteringSettings, BGMPreset } from "@/types";

interface AudioEditorProps {
  assetId?: string | null;
  initialAudioUrl?: string | null;
  poetryVerses?: string[];
  poetName?: string | null;
  title?: string | null;
  onMasteringComplete?: (newAssetId: string, newUrl: string) => void;
}

const DEFAULT_BGM_PRESETS: BGMPreset[] = [
  {
    id: "none",
    name: "None (Acapella / تنہا آواز)",
    category: "none",
    description: "Pure vocal without instrumental accompaniment",
  },
  {
    id: "rubab-meditative",
    name: "Rubab Meditative (مراقبہ رباب)",
    category: "acoustic",
    description: "Gentle Afghan/Pashto rubab plucks with warm low-mids",
  },
  {
    id: "sitar-twilight",
    name: "Sitar Twilight (شامِ ستار)",
    category: "classical",
    description: "Atmospheric evening ragas with gentle resonance",
  },
  {
    id: "flute-melancholy",
    name: "Bansuri Flute (بانسری درد)",
    category: "wind",
    description: "Soulful wooden flute melodies for melancholic couplets",
  },
  {
    id: "lofi-rain",
    name: "Lo-Fi Rain & Vinyl (بارش اور دھیمی دھن)",
    category: "modern",
    description: "Cozy vinyl crackle and ambient rain drops for modern reels",
  },
];

export function AudioEditor({
  assetId,
  initialAudioUrl,
  poetryVerses = [],
  poetName,
  title,
  onMasteringComplete,
}: AudioEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const waveSurferRef = useRef<any>(null);

  // Playback State
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [activeVerseIndex, setActiveVerseIndex] = useState<number | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(initialAudioUrl || null);
  const [currentAssetId, setCurrentAssetId] = useState<string | null>(assetId || null);

  // DSP Controls State
  const [settings, setSettings] = useState<AudioMasteringSettings>({
    speed: 1.0,
    pitch: 0.0,
    warmth_db: 2.5,
    air_db: 1.5,
    reverb_wet: 0.15,
    room_size: 0.5,
    enable_compression: true,
    compressor_threshold_db: -16.0,
    bgm_preset_id: "none",
    bgm_volume: 0.25,
    ducking_depth_db: -14.0,
  });

  const [bgmPresets, setBgmPresets] = useState<BGMPreset[]>(DEFAULT_BGM_PRESETS);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processStatus, setProcessStatus] = useState<string | null>(null);
  const [useFallbackAudio, setUseFallbackAudio] = useState(false);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  // Load BGM presets from backend if available
  useEffect(() => {
    let isMounted = true;
    api
      .getBgmPresets()
      .then((presets) => {
        if (isMounted && presets && presets.length > 0) {
          setBgmPresets([DEFAULT_BGM_PRESETS[0], ...presets]);
        }
      })
      .catch(() => {
        // Fallback to defaults
      });
    return () => {
      isMounted = false;
    };
  }, []);

  // Sync initialAudioUrl and assetId
  useEffect(() => {
    if (initialAudioUrl) {
      setAudioUrl(initialAudioUrl);
    }
  }, [initialAudioUrl]);

  useEffect(() => {
    if (assetId) {
      setCurrentAssetId(assetId);
    }
  }, [assetId]);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current || !audioUrl) return;

    let ws: any = null;

    const initWaveSurfer = async () => {
      try {
        const WaveSurfer = (await import("wavesurfer.js")).default;
        if (!containerRef.current) return;

        ws = WaveSurfer.create({
          container: containerRef.current,
          waveColor: "#334155",
          progressColor: "#F59E0B",
          cursorColor: "#10B981",
          barWidth: 2,
          barGap: 3,
          barRadius: 2,
          height: 84,
          url: audioUrl,
        });

        ws.on("ready", () => {
          setDuration(ws.getDuration());
          setIsPlaying(false);
        });

        ws.on("play", () => setIsPlaying(true));
        ws.on("pause", () => setIsPlaying(false));
        ws.on("timeupdate", (time: number) => {
          setCurrentTime(time);
          const totalDur = ws.getDuration();
          if (poetryVerses.length > 0 && totalDur > 0) {
            const verseDuration = totalDur / poetryVerses.length;
            const idx = Math.min(
              Math.floor(time / verseDuration),
              poetryVerses.length - 1
            );
            setActiveVerseIndex(idx);
          }
        });

        ws.on("finish", () => {
          setIsPlaying(false);
          setCurrentTime(0);
        });

        ws.on("error", () => {
          setUseFallbackAudio(true);
        });

        waveSurferRef.current = ws;
      } catch {
        setUseFallbackAudio(true);
      }
    };

    initWaveSurfer();

    return () => {
      if (ws) {
        try {
          ws.destroy();
        } catch {
          // cleanup
        }
      }
    };
  }, [audioUrl, poetryVerses.length]);

  const togglePlay = () => {
    if (waveSurferRef.current && !useFallbackAudio) {
      try {
        waveSurferRef.current.playPause();
        return;
      } catch {
        // fallback
      }
    }
    if (audioElementRef.current) {
      if (isPlaying) {
        audioElementRef.current.pause();
        setIsPlaying(false);
      } else {
        audioElementRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleStop = () => {
    if (waveSurferRef.current && !useFallbackAudio) {
      try {
        waveSurferRef.current.stop();
        setIsPlaying(false);
        setCurrentTime(0);
        return;
      } catch {
        // fallback
      }
    }
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current.currentTime = 0;
      setIsPlaying(false);
      setCurrentTime(0);
    }
  };

  const seekToVerse = (index: number) => {
    if (poetryVerses.length === 0 || duration === 0) return;
    const targetTime = (index / poetryVerses.length) * duration;
    setActiveVerseIndex(index);
    if (waveSurferRef.current && !useFallbackAudio) {
      try {
        waveSurferRef.current.seekTo(index / poetryVerses.length);
        return;
      } catch {
        // fallback
      }
    }
    if (audioElementRef.current) {
      audioElementRef.current.currentTime = targetTime;
      setCurrentTime(targetTime);
    }
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainder = Math.floor(secs % 60);
    return `${mins.toString().padStart(2, "0")}:${remainder
      .toString()
      .padStart(2, "0")}`;
  };

  // Master Audio DSP Request
  const handleApplyMastering = async () => {
    if (!currentAssetId) {
      setProcessStatus("No audio asset available to master.");
      return;
    }

    setIsProcessing(true);
    setProcessStatus("Applying Warm EQ, Reverb & Compressor...");

    try {
      const payload: AudioMasteringRequest = {
        asset_id: currentAssetId,
        speed: settings.speed,
        pitch: settings.pitch,
        warmth_db: settings.warmth_db,
        air_db: settings.air_db,
        reverb_wet: settings.reverb_wet,
        room_size: settings.room_size,
        enable_compression: settings.enable_compression,
        compressor_threshold_db: settings.compressor_threshold_db,
        bgm_preset_id:
          settings.bgm_preset_id === "none" ? null : settings.bgm_preset_id,
        bgm_volume: settings.bgm_volume,
        ducking_depth_db: settings.ducking_depth_db,
      };

      const res = await api.masterAudio(payload);
      setCurrentAssetId(res.asset_id);
      setAudioUrl(res.stream_url);
      setProcessStatus("Mastering applied successfully! Audio refreshed.");
      if (onMasteringComplete) {
        onMasteringComplete(res.asset_id, res.stream_url);
      }
    } catch (err: any) {
      setProcessStatus(`Mastering failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Trim Silence Request
  const handleTrimSilence = async () => {
    if (!currentAssetId) {
      setProcessStatus("No audio asset selected.");
      return;
    }

    setIsProcessing(true);
    setProcessStatus("Trimming leading/trailing silence...");

    try {
      const res = await api.trimSilence({
        asset_id: currentAssetId,
        threshold_db: -38.0,
      });
      setCurrentAssetId(res.asset_id);
      setAudioUrl(res.stream_url);
      setProcessStatus("Silence trimmed successfully!");
      if (onMasteringComplete) {
        onMasteringComplete(res.asset_id, res.stream_url);
      }
    } catch (err: any) {
      setProcessStatus(`Trimming failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-studio-card border border-studio-border rounded-3xl p-6 sm:p-8 shadow-studio space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-studio-border pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-studio-gold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Acoustic Mastering & Waveform Editor</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-studio-text mt-1">
            {title ? `Audio: ${title}` : "Interactive Audio Studio"}
          </h2>
          {poetName && (
            <p className="text-xs text-studio-muted">
              Poet: <span className="text-studio-gold font-medium">{poetName}</span>
            </p>
          )}
        </div>

        {/* Action Quick Pills */}
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={handleTrimSilence}
            disabled={isProcessing || !currentAssetId}
            className="px-3.5 py-2 rounded-xl bg-studio-surface border border-studio-border text-xs font-medium text-studio-text hover:border-studio-amber transition-colors flex items-center gap-2 cursor-pointer disabled:opacity-50"
            title="Remove quiet padding at start and end"
          >
            <Scissors className="w-3.5 h-3.5 text-studio-amber" />
            <span>Trim Silence</span>
          </button>

          {audioUrl && (
            <a
              href={audioUrl}
              download="mastered_urdu_voiceover.wav"
              className="px-3.5 py-2 rounded-xl bg-studio-surface border border-studio-border text-xs font-medium text-studio-text hover:border-studio-emerald transition-colors flex items-center gap-2"
            >
              <Download className="w-3.5 h-3.5 text-studio-emerald" />
              <span>Export WAV</span>
            </a>
          )}
        </div>
      </div>

      {/* Waveform Player Section */}
      <div className="bg-studio-surface/80 border border-studio-border rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between text-xs text-studio-muted">
          <div className="flex items-center gap-2">
            <Music2 className="w-4 h-4 text-studio-gold" />
            <span className="font-mono text-studio-text">
              {formatTime(currentTime)} / {formatTime(duration || 0)}
            </span>
          </div>
          <span className="text-[11px] text-studio-muted">
            {audioUrl ? "24,000 Hz • 32-bit Float • Mono" : "No Audio Loaded"}
          </span>
        </div>

        {/* Wavesurfer Container */}
        <div
          ref={containerRef}
          data-testid="waveform-container"
          className={`w-full min-h-[84px] bg-studio-bg/60 rounded-xl overflow-hidden border border-studio-border/50 ${
            useFallbackAudio ? "hidden" : "block"
          }`}
        />

        {/* Fallback audio element for jsdom or non-canvas environments */}
        {useFallbackAudio && audioUrl && (
          <audio
            ref={audioElementRef}
            src={audioUrl}
            onTimeUpdate={(e) => setCurrentTime((e.target as any).currentTime)}
            onLoadedMetadata={(e) => setDuration((e.target as any).duration)}
            onEnded={() => setIsPlaying(false)}
            controls
            className="w-full h-10 mt-2"
          />
        )}

        {/* Transport Controls */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={togglePlay}
              disabled={!audioUrl}
              aria-label={isPlaying ? "Pause audio" : "Play audio"}
              className="w-11 h-11 rounded-full bg-studio-gold hover:opacity-95 text-studio-bg flex items-center justify-center shadow-gold transition-transform active:scale-95 disabled:opacity-40 cursor-pointer"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 fill-current" />
              ) : (
                <Play className="w-5 h-5 fill-current ml-0.5" />
              )}
            </button>

            <button
              type="button"
              onClick={handleStop}
              disabled={!audioUrl}
              aria-label="Stop audio"
              className="w-10 h-10 rounded-full bg-studio-card border border-studio-border hover:border-studio-amber text-studio-muted hover:text-studio-text flex items-center justify-center transition-colors disabled:opacity-40 cursor-pointer"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          </div>

          <div className="text-xs text-studio-muted text-right">
            <span>Status: </span>
            <span className="text-studio-emerald font-medium">
              {isPlaying ? "Playing" : "Paused"}
            </span>
          </div>
        </div>

        {/* Verse Timeline Navigation */}
        {poetryVerses.length > 0 && (
          <div className="pt-3 border-t border-studio-border/60">
            <div className="text-[11px] font-semibold text-studio-muted uppercase tracking-wider mb-2">
              Poetry Stanza Markers (شعر پر جائیں)
            </div>
            <div className="flex flex-wrap gap-2">
              {poetryVerses.map((verse, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => seekToVerse(idx)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-urdu transition-all text-right flex items-center gap-2 cursor-pointer border ${
                    activeVerseIndex === idx
                      ? "bg-studio-gold/15 border-studio-gold text-studio-gold font-bold shadow-sm"
                      : "bg-studio-card/80 border-studio-border text-studio-text hover:border-studio-gold/40"
                  }`}
                >
                  <span className="text-[10px] font-mono text-studio-muted">
                    #{idx + 1}
                  </span>
                  <span className="truncate max-w-[200px]">{verse}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* DSP Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Equalization & Timbre */}
        <div className="p-5 rounded-2xl bg-studio-surface border border-studio-border space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-studio-gold uppercase tracking-wider">
            <Sliders className="w-3.5 h-3.5" />
            <span>Parametric Equalization</span>
          </div>

          {/* Warmth EQ */}
          <div>
            <div className="flex justify-between text-xs text-studio-text mb-1">
              <span>Warmth (بیس کی گہرائی)</span>
              <span className="font-mono text-studio-gold">+{settings.warmth_db} dB</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="8.0"
              step="0.5"
              value={settings.warmth_db}
              onChange={(e) =>
                setSettings({ ...settings, warmth_db: parseFloat(e.target.value) })
              }
              className="w-full accent-studio-gold cursor-pointer"
            />
            <p className="text-[10px] text-studio-muted mt-0.5">
              Enhances chest resonance (200Hz) for deep classical poetry recitation.
            </p>
          </div>

          {/* Air EQ */}
          <div>
            <div className="flex justify-between text-xs text-studio-text mb-1">
              <span>Air & Breath (شائستگی)</span>
              <span className="font-mono text-studio-gold">+{settings.air_db} dB</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="6.0"
              step="0.5"
              value={settings.air_db}
              onChange={(e) =>
                setSettings({ ...settings, air_db: parseFloat(e.target.value) })
              }
              className="w-full accent-studio-gold cursor-pointer"
            />
            <p className="text-[10px] text-studio-muted mt-0.5">
              High-shelf boost (8kHz) for breathy diction and emotional intimacy.
            </p>
          </div>
        </div>

        {/* Mushaira Reverb & Space */}
        <div className="p-5 rounded-2xl bg-studio-surface border border-studio-border space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-studio-gold uppercase tracking-wider">
            <Layers className="w-3.5 h-3.5" />
            <span>Mushaira Hall Acoustic Space</span>
          </div>

          {/* Reverb Wet Mix */}
          <div>
            <div className="flex justify-between text-xs text-studio-text mb-1">
              <span>Reverb Wet Mix (مشاعرہ گونج)</span>
              <span className="font-mono text-studio-gold">
                {Math.round(settings.reverb_wet * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.5"
              step="0.05"
              value={settings.reverb_wet}
              onChange={(e) =>
                setSettings({ ...settings, reverb_wet: parseFloat(e.target.value) })
              }
              className="w-full accent-studio-gold cursor-pointer"
            />
            <p className="text-[10px] text-studio-muted mt-0.5">
              Vectorized Schroeder Schroeder reverberator mimicking carpeted mushaira halls.
            </p>
          </div>

          {/* Room Size */}
          <div>
            <div className="flex justify-between text-xs text-studio-text mb-1">
              <span>Room Scale (ہال کی وسعت)</span>
              <span className="font-mono text-studio-gold">
                {Math.round(settings.room_size * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={settings.room_size}
              onChange={(e) =>
                setSettings({ ...settings, room_size: parseFloat(e.target.value) })
              }
              className="w-full accent-studio-gold cursor-pointer"
            />
          </div>
        </div>

        {/* Background Music Preset */}
        <div className="p-5 rounded-2xl bg-studio-surface border border-studio-border space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-studio-gold uppercase tracking-wider">
            <Music2 className="w-3.5 h-3.5" />
            <span>Background Music (پس پردہ ساز)</span>
          </div>

          <div>
            <label className="block text-xs text-studio-text mb-1.5">
              Select Curated Instrument
            </label>
            <select
              value={settings.bgm_preset_id || "none"}
              onChange={(e) =>
                setSettings({ ...settings, bgm_preset_id: e.target.value })
              }
              className="w-full px-3 py-2.5 rounded-xl bg-studio-card border border-studio-border text-studio-text text-xs focus:outline-none focus:border-studio-gold cursor-pointer"
            >
              {bgmPresets.map((preset) => (
                <option key={preset.id} value={preset.id}>
                  {preset.name}
                </option>
              ))}
            </select>
          </div>

          {settings.bgm_preset_id !== "none" && (
            <div className="space-y-3 pt-1">
              <div>
                <div className="flex justify-between text-xs text-studio-text mb-1">
                  <span>Music Level</span>
                  <span className="font-mono text-studio-gold">
                    {Math.round(settings.bgm_volume * 100)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={settings.bgm_volume}
                  onChange={(e) =>
                    setSettings({ ...settings, bgm_volume: parseFloat(e.target.value) })
                  }
                  className="w-full accent-studio-gold cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs text-studio-text mb-1">
                  <span>Voice Ducking Depth</span>
                  <span className="font-mono text-studio-gold">
                    {settings.ducking_depth_db} dB
                  </span>
                </div>
                <input
                  type="range"
                  min="-30"
                  max="-3"
                  step="1"
                  value={settings.ducking_depth_db}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      ducking_depth_db: parseFloat(e.target.value),
                    })
                  }
                  className="w-full accent-studio-gold cursor-pointer"
                />
                <p className="text-[10px] text-studio-muted mt-0.5">
                  Automatically dips music volume when poetry is spoken.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Dynamic Compressor */}
        <div className="p-5 rounded-2xl bg-studio-surface border border-studio-border space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-studio-gold uppercase tracking-wider">
              <Volume2 className="w-3.5 h-3.5" />
              <span>Broadcast Vocal Compressor</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enable_compression}
                onChange={(e) =>
                  setSettings({ ...settings, enable_compression: e.target.checked })
                }
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-studio-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-studio-gold"></div>
            </label>
          </div>

          <div>
            <div className="flex justify-between text-xs text-studio-text mb-1">
              <span>Threshold</span>
              <span className="font-mono text-studio-gold">
                {settings.compressor_threshold_db} dB
              </span>
            </div>
            <input
              type="range"
              min="-40"
              max="0"
              step="1"
              disabled={!settings.enable_compression}
              value={settings.compressor_threshold_db}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  compressor_threshold_db: parseFloat(e.target.value),
                })
              }
              className="w-full accent-studio-gold cursor-pointer disabled:opacity-40"
            />
            <p className="text-[10px] text-studio-muted mt-0.5">
              Even out dynamic range so soft whispering verses remain crystal clear.
            </p>
          </div>
        </div>
      </div>

      {/* Status banner */}
      {processStatus && (
        <div className="p-3.5 rounded-xl bg-studio-surface border border-studio-border text-xs text-studio-muted flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-studio-emerald" />
            <span>{processStatus}</span>
          </div>
          <button
            type="button"
            onClick={() => setProcessStatus(null)}
            className="text-studio-muted hover:text-studio-text text-xs ml-2 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Apply Mastering Action Button */}
      <button
        type="button"
        onClick={handleApplyMastering}
        disabled={isProcessing || !currentAssetId}
        className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-studio-gold via-studio-amber to-studio-gold hover:opacity-95 text-studio-bg font-bold text-sm shadow-gold transition-all duration-200 flex items-center justify-center gap-2.5 cursor-pointer disabled:opacity-50"
      >
        <Sparkles className="w-4 h-4" />
        <span>
          {isProcessing ? "Rendering DSP Master..." : "Apply DSP Mastering Chain"}
        </span>
        <span className="font-nastaliq text-base font-bold pr-1">
          (ماسٹرنگ لاگو کریں)
        </span>
      </button>
    </div>
  );
}

