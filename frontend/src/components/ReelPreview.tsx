"use client";

import { useEffect, useRef, useState } from "react";
import {
  Film,
  Sparkles,
  Download,
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  Palette,
  Type,
  Maximize2,
  Video,
} from "lucide-react";
import { api } from "@/services/api";
import { ReelRenderRequest, ReelThemePreset } from "@/types";

interface ReelPreviewProps {
  projectId?: string | null;
  audioAssetId?: string | null;
  poetryVerses?: string[];
  title?: string | null;
  poetName?: string | null;
  initialVideoUrl?: string | null;
  onRenderComplete?: (newVideoId: string, newUrl: string) => void;
}

const DEFAULT_THEMES: ReelThemePreset[] = [
  {
    id: "velvet-gold",
    name: "Velvet & Gold (شاہانہ مخمل و زر)",
    description: "Deep midnight navy with royal gold calligraphy accents",
    bg_color_hex: "0x080B14",
    accent_color_hex: "0xF59E0B",
  },
  {
    id: "emerald-night",
    name: "Mughal Emerald (مغلیہ زمرد)",
    description: "Rich atmospheric jade-emerald for soulful classic ghazals",
    bg_color_hex: "0x06140E",
    accent_color_hex: "0x10B981",
  },
  {
    id: "candlelight",
    name: "Candlelit Amber (شمع و محفل)",
    description: "Warm incandescent sepia and dark charcoal for romantic verses",
    bg_color_hex: "0x140B07",
    accent_color_hex: "0xFB923C",
  },
  {
    id: "monochrome-rain",
    name: "Noir Rain (سیاہ و سفید بارش)",
    description: "Moody high-contrast slate for melancholic modern couplets",
    bg_color_hex: "0x0A0C10",
    accent_color_hex: "0x94A3B8",
  },
];

export function ReelPreview({
  projectId,
  audioAssetId,
  poetryVerses = [],
  title,
  poetName,
  initialVideoUrl,
  onRenderComplete,
}: ReelPreviewProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [themes, setThemes] = useState<ReelThemePreset[]>(DEFAULT_THEMES);
  const [selectedThemeId, setSelectedThemeId] = useState("velvet-gold");
  const [fontSize, setFontSize] = useState(60);
  const [enableKaraoke, setEnableKaraoke] = useState(true);
  const [fps, setFps] = useState(30);

  // Playback & Render State
  const [videoUrl, setVideoUrl] = useState<string | null>(initialVideoUrl || null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRendering, setIsRendering] = useState(false);
  const [renderStatus, setRenderStatus] = useState<string | null>(null);

  // Active theme object
  const activeTheme =
    themes.find((t) => t.id === selectedThemeId) || themes[0];

  useEffect(() => {
    let isMounted = true;
    api
      .getReelThemes()
      .then((data) => {
        if (isMounted && data && data.length > 0) {
          setThemes(data);
        }
      })
      .catch(() => {
        // Fallback to default presets
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (initialVideoUrl) {
      setVideoUrl(initialVideoUrl);
    }
  }, [initialVideoUrl]);

  const toggleVideoPlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleRenderReel = async () => {
    if (!projectId || !audioAssetId) {
      setRenderStatus("Please synthesize and master audio before rendering reel video.");
      return;
    }

    setIsRendering(true);
    setRenderStatus("Starting FFmpeg 9:16 vertical render engine...");

    try {
      const payload: ReelRenderRequest = {
        project_id: projectId,
        audio_asset_id: audioAssetId,
        theme_id: selectedThemeId,
        font_size: fontSize,
        enable_karaoke: enableKaraoke,
        fps: fps,
      };

      const res = await api.renderReel(payload);
      setVideoUrl(res.stream_url);
      setRenderStatus("Reel rendered successfully! 1080x1920 MP4 ready for preview & export.");
      if (onRenderComplete) {
        onRenderComplete(res.video_asset_id, res.stream_url);
      }
    } catch (err: any) {
      setRenderStatus(`Rendering failed: ${err.message || "Unknown error"}`);
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <div className="bg-studio-card border border-studio-border rounded-3xl p-6 sm:p-8 shadow-studio space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-studio-border pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-studio-gold uppercase tracking-wider">
            <Film className="w-3.5 h-3.5" />
            <span>9:16 Vertical Reel Production</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-studio-text mt-1">
            {title ? `Reel: ${title}` : "Cinematic Reel Studio"}
          </h2>
          {poetName && (
            <p className="text-xs text-studio-muted">
              Poet: <span className="text-studio-gold font-medium">{poetName}</span>
            </p>
          )}
        </div>

        {videoUrl && (
          <a
            href={videoUrl}
            download={`${title || "urdu_poetry"}_reel.mp4`}
            className="px-4 py-2.5 rounded-xl bg-studio-gold hover:opacity-95 text-studio-bg font-bold text-xs shadow-gold transition-all flex items-center gap-2 self-start sm:self-center cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export Reel (MP4)</span>
          </a>
        )}
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: 9:16 Vertical Smartphone Preview (5 cols) */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="text-[11px] font-semibold text-studio-muted uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Video className="w-3.5 h-3.5 text-studio-gold" />
            <span>1080x1920 Vertical Feed Preview</span>
          </div>

          {/* Smartphone Frame Container */}
          <div className="relative w-[280px] sm:w-[320px] aspect-[9/16] rounded-[36px] bg-studio-bg border-[6px] border-studio-border shadow-2xl overflow-hidden flex flex-col justify-between p-6">
            {/* Top Phone Sensor Island */}
            <div className="absolute top-2 left-1/2 -translate-x-1/2 w-20 h-4 bg-black/60 rounded-full z-20 pointer-events-none" />

            {/* Video Player or Live Typography Simulation */}
            {videoUrl ? (
              <div className="absolute inset-0 z-10 bg-black flex items-center justify-center">
                <video
                  ref={videoRef}
                  src={videoUrl}
                  playsInline
                  loop
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  className="w-full h-full object-cover"
                />
                {/* Floating Play/Pause Overlay */}
                <button
                  type="button"
                  onClick={toggleVideoPlay}
                  aria-label={isPlaying ? "Pause video" : "Play video"}
                  className="absolute inset-0 flex items-center justify-center bg-black/25 opacity-0 hover:opacity-100 transition-opacity cursor-pointer"
                >
                  <div className="w-14 h-14 rounded-full bg-studio-gold text-studio-bg flex items-center justify-center shadow-gold">
                    {isPlaying ? (
                      <Pause className="w-6 h-6 fill-current" />
                    ) : (
                      <Play className="w-6 h-6 fill-current ml-0.5" />
                    )}
                  </div>
                </button>
              </div>
            ) : (
              /* Simulated Live Typography Canvas */
              <div
                className="absolute inset-0 z-0 flex flex-col justify-between p-6 text-center transition-colors duration-500"
                style={{
                  backgroundColor:
                    selectedThemeId === "velvet-gold"
                      ? "#080B14"
                      : selectedThemeId === "emerald-night"
                      ? "#06140E"
                      : selectedThemeId === "candlelight"
                      ? "#140B07"
                      : "#0A0C10",
                }}
              >
                {/* Atmospheric Glow */}
                <div
                  className="absolute inset-0 opacity-30 pointer-events-none"
                  style={{
                    background: `radial-gradient(circle at center, #${activeTheme.accent_color_hex.replace(
                      "0x",
                      ""
                    )} 0%, transparent 70%)`,
                  }}
                />

                {/* Top Section: Title & Poet */}
                <div className="pt-6 relative z-10">
                  <div
                    className="font-nastaliq text-base font-bold text-shadow"
                    style={{
                      color: `#${activeTheme.accent_color_hex.replace("0x", "")}`,
                    }}
                  >
                    {title || "الفاظ اسٹوڈیو"}
                  </div>
                  {poetName && (
                    <div className="font-nastaliq text-xs text-white/80 mt-1">
                      شاعر: {poetName}
                    </div>
                  )}
                </div>

                {/* Center Section: Animated Poetry Verse */}
                <div className="my-auto relative z-10 px-2 space-y-4">
                  {poetryVerses.length > 0 ? (
                    poetryVerses.slice(0, 2).map((verse, idx) => (
                      <div
                        key={idx}
                        className="font-nastaliq text-lg sm:text-xl font-bold leading-relaxed text-white text-shadow drop-shadow-md"
                      >
                        {verse}
                      </div>
                    ))
                  ) : (
                    <div className="font-nastaliq text-lg text-white/70">
                      دل ناداں تجھے ہوا کیا ہے
                    </div>
                  )}
                </div>

                {/* Bottom Section: Branding Watermark */}
                <div className="pb-4 relative z-10 text-[10px] text-white/40 tracking-wider">
                  AlfaazStudio • 9:16 Reel
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Rendering & Aesthetics Controls (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Aesthetic Theme Selection */}
          <div className="p-5 rounded-2xl bg-studio-surface border border-studio-border space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold text-studio-gold uppercase tracking-wider">
              <Palette className="w-3.5 h-3.5" />
              <span>Aesthetic Visual Theme</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {themes.map((theme) => (
                <button
                  key={theme.id}
                  type="button"
                  onClick={() => setSelectedThemeId(theme.id)}
                  className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                    selectedThemeId === theme.id
                      ? "bg-studio-gold/15 border-studio-gold shadow-sm"
                      : "bg-studio-card/80 border-studio-border hover:border-studio-gold/40"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-studio-text">
                      {theme.name}
                    </span>
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-white/20"
                      style={{
                        backgroundColor: `#${theme.accent_color_hex.replace("0x", "")}`,
                      }}
                    />
                  </div>
                  <p className="text-[11px] text-studio-muted leading-tight">
                    {theme.description}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Subtitle & Typography Controls */}
          <div className="p-5 rounded-2xl bg-studio-surface border border-studio-border space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold text-studio-gold uppercase tracking-wider">
              <Type className="w-3.5 h-3.5" />
              <span>Nastaliq Subtitle Typography</span>
            </div>

            {/* Font Size Slider */}
            <div>
              <div className="flex justify-between text-xs text-studio-text mb-1">
                <span>Calligraphy Scale (فونٹ کا سائز)</span>
                <span className="font-mono text-studio-gold">{fontSize} pt</span>
              </div>
              <input
                type="range"
                min="40"
                max="80"
                step="2"
                value={fontSize}
                onChange={(e) => setFontSize(parseInt(e.target.value, 10))}
                className="w-full accent-studio-gold cursor-pointer"
              />
            </div>

            {/* Karaoke Word Highlight Toggle */}
            <div className="flex items-center justify-between pt-2 border-t border-studio-border">
              <div>
                <span className="text-xs font-medium text-studio-text block">
                  Kinetic Karaoke Highlight
                </span>
                <span className="text-[11px] text-studio-muted">
                  Highlights each word in sync with speech rhythm
                </span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableKaraoke}
                  onChange={(e) => setEnableKaraoke(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-studio-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-studio-gold"></div>
              </label>
            </div>
          </div>

          {/* Status Message */}
          {renderStatus && (
            <div className="p-3.5 rounded-xl bg-studio-surface border border-studio-border text-xs text-studio-muted flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-studio-emerald" />
                <span>{renderStatus}</span>
              </div>
              <button
                type="button"
                onClick={() => setRenderStatus(null)}
                className="text-studio-muted hover:text-studio-text text-xs ml-2 cursor-pointer"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Primary Render Action */}
          <button
            type="button"
            onClick={handleRenderReel}
            disabled={isRendering || !audioAssetId}
            className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-studio-gold via-studio-amber to-studio-gold hover:opacity-95 text-studio-bg font-bold text-sm shadow-gold transition-all duration-200 flex items-center justify-center gap-2.5 cursor-pointer disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>
              {isRendering
                ? "Rendering 1080x1920 MP4 Video..."
                : "Render 9:16 Vertical Reel (MP4)"}
            </span>
            <span className="font-nastaliq text-base font-bold pr-1">
              (ریل ویڈیو تیار کریں)
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
