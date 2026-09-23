"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Mic,
  Square,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Volume2,
  CheckCircle2,
  X,
  Sliders,
  AlertCircle,
} from "lucide-react";

interface VoiceRecorderProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveRecording: (file: File) => void;
}

type RecordingState = "idle" | "recording" | "paused" | "stopped";
type EQPreset = "none" | "warm" | "clear" | "deep";

export function VoiceRecorder({
  isOpen,
  onClose,
  onSaveRecording,
}: VoiceRecorderProps) {
  const [state, setState] = useState<RecordingState>("idle");
  const [duration, setDuration] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Audio & Streams
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Raw and processed audio
  const [rawAudioUrl, setRawAudioUrl] = useState<string | null>(null);
  const [processedAudioUrl, setProcessedAudioUrl] = useState<string | null>(null);
  const [processedBlob, setProcessedBlob] = useState<Blob | null>(null);
  const [audioBuffer, setAudioBuffer] = useState<AudioBuffer | null>(null);

  // Voice Enhancement settings
  const [noiseReduction, setNoiseReduction] = useState(true);
  const [normalizeVolume, setNormalizeVolume] = useState(true);
  const [eqPreset, setEqPreset] = useState<EQPreset>("warm");
  const [isEnhancing, setIsEnhancing] = useState(false);

  // Audio Playback
  const [isPlaying, setIsPlaying] = useState(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  // Canvas visualizer
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Clean up resources on unmount or close
  useEffect(() => {
    return () => {
      cleanupStream();
    };
  }, []);

  const cleanupStream = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
  };

  const resetAll = () => {
    cleanupStream();
    setState("idle");
    setDuration(0);
    setErrorMsg(null);
    setRawAudioUrl(null);
    setProcessedAudioUrl(null);
    setProcessedBlob(null);
    setAudioBuffer(null);
    setIsPlaying(false);
  };

  const startVisualizer = (stream: MediaStream) => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      source.connect(analyser);
      analyserRef.current = analyser;

      const canvas = canvasRef.current;
      if (!canvas) return;
      const canvasCtx = canvas.getContext("2d");
      if (!canvasCtx) return;

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const draw = () => {
        animationFrameRef.current = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);

        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        const barWidth = (canvas.width / bufferLength) * 2;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const barHeight = (dataArray[i] / 255) * canvas.height;
          canvasCtx.fillStyle = "#F59E0B";
          canvasCtx.fillRect(
            x,
            canvas.height - barHeight,
            barWidth - 2,
            barHeight
          );
          x += barWidth;
        }
      };

      draw();
    } catch {
      // Visualizer is optional
    }
  };

  const startRecording = async () => {
    setErrorMsg(null);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: false,
          autoGainControl: false,
        },
      });

      mediaStreamRef.current = stream;
      startVisualizer(stream);

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const rawBlob = new Blob(audioChunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        const url = URL.createObjectURL(rawBlob);
        setRawAudioUrl(url);

        // Decode raw audio to AudioBuffer for enhancement & WAV conversion
        try {
          const arrayBuffer = await rawBlob.arrayBuffer();
          const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
          const decodeCtx = new AudioCtx();
          const decoded = await decodeCtx.decodeAudioData(arrayBuffer);
          setAudioBuffer(decoded);
          decodeCtx.close();
          // Auto-apply initial enhancements
          enhanceAudio(decoded, noiseReduction, normalizeVolume, eqPreset);
        } catch (err: any) {
          setErrorMsg("Could not decode audio. Please retake recording.");
        }
      };

      recorder.start(100);
      setState("recording");

      // Duration Timer
      setDuration(0);
      timerIntervalRef.current = setInterval(() => {
        setDuration((prev) => {
          if (prev >= 60) {
            stopRecording();
            return 60;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err: any) {
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setErrorMsg("Microphone permission was denied. Please allow microphone access in your browser settings.");
      } else {
        setErrorMsg(`Failed to access microphone: ${err.message || "Unknown error"}`);
      }
      setState("idle");
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && state === "recording") {
      mediaRecorderRef.current.pause();
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      setState("paused");
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && state === "paused") {
      mediaRecorderRef.current.resume();
      timerIntervalRef.current = setInterval(() => {
        setDuration((prev) => {
          if (prev >= 60) {
            stopRecording();
            return 60;
          }
          return prev + 1;
        });
      }, 1000);
      setState("recording");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && (state === "recording" || state === "paused")) {
      mediaRecorderRef.current.stop();
      cleanupStream();
      setState("stopped");
    }
  };

  // Web Audio API DSP Enhancement Chain & WAV Export
  const enhanceAudio = async (
    sourceBuffer: AudioBuffer | null,
    applyNoiseCut: boolean,
    applyNorm: boolean,
    preset: EQPreset
  ) => {
    const buf = sourceBuffer || audioBuffer;
    if (!buf) return;

    setIsEnhancing(true);

    try {
      const targetSampleRate = 16000; // Optimal for Voice Cloning (F5-TTS, Melo, Piper)
      const offlineCtx = new OfflineAudioContext(
        1,
        Math.ceil(buf.duration * targetSampleRate),
        targetSampleRate
      );

      // Create BufferSource
      const source = offlineCtx.createBufferSource();
      source.buffer = buf;

      let lastNode: AudioNode = source;

      // 1. High-Pass Filter (Low-end rumble and pop noise reduction: 80Hz)
      if (applyNoiseCut) {
        const highpass = offlineCtx.createBiquadFilter();
        highpass.type = "highpass";
        highpass.frequency.value = 80;
        highpass.Q.value = 0.707;
        lastNode.connect(highpass);
        lastNode = highpass;
      }

      // 2. EQ Presets
      if (preset === "warm") {
        const warmFilter = offlineCtx.createBiquadFilter();
        warmFilter.type = "peaking";
        warmFilter.frequency.value = 250;
        warmFilter.Q.value = 1.0;
        warmFilter.gain.value = 3.5; // +3.5dB low-mid body
        lastNode.connect(warmFilter);
        lastNode = warmFilter;
      } else if (preset === "clear") {
        const clearFilter = offlineCtx.createBiquadFilter();
        clearFilter.type = "highshelf";
        clearFilter.frequency.value = 4500;
        clearFilter.gain.value = 3.0; // +3dB clarity
        lastNode.connect(clearFilter);
        lastNode = clearFilter;
      } else if (preset === "deep") {
        const deepFilter = offlineCtx.createBiquadFilter();
        deepFilter.type = "lowshelf";
        deepFilter.frequency.value = 150;
        deepFilter.gain.value = 4.0; // +4dB deep resonance
        lastNode.connect(deepFilter);
        lastNode = deepFilter;
      }

      // Connect to destination
      lastNode.connect(offlineCtx.destination);
      source.start(0);

      // Render audio
      const renderedBuffer = await offlineCtx.startRendering();

      // 3. Peak Normalization (if enabled)
      let channelData = renderedBuffer.getChannelData(0);
      if (applyNorm) {
        let maxPeak = 0;
        for (let i = 0; i < channelData.length; i++) {
          const abs = Math.abs(channelData[i]);
          if (abs > maxPeak) maxPeak = abs;
        }

        if (maxPeak > 0.01) {
          const targetPeak = 0.95; // -0.5 dBFS
          const gain = targetPeak / maxPeak;
          const normalized = new Float32Array(channelData.length);
          for (let i = 0; i < channelData.length; i++) {
            normalized[i] = channelData[i] * gain;
          }
          channelData = normalized;
        }
      }

      // Convert rendered channel to 16-bit PCM WAV Blob
      const wavBlob = encodeWavBlob(channelData, targetSampleRate);
      const url = URL.createObjectURL(wavBlob);

      setProcessedBlob(wavBlob);
      setProcessedAudioUrl(url);
    } catch (err: any) {
      setErrorMsg(`Enhancement failed: ${err.message}`);
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleApplySettings = () => {
    if (audioBuffer) {
      enhanceAudio(audioBuffer, noiseReduction, normalizeVolume, eqPreset);
    }
  };

  const togglePlayback = () => {
    if (!audioPlayerRef.current) return;
    if (isPlaying) {
      audioPlayerRef.current.pause();
      setIsPlaying(false);
    } else {
      audioPlayerRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleUseRecording = () => {
    if (!processedBlob) return;
    const file = new File(
      [processedBlob],
      `recorded_voice_${Date.now()}.wav`,
      { type: "audio/wav" }
    );
    onSaveRecording(file);
    resetAll();
    onClose();
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-3xl bg-studio-card border border-studio-border p-6 sm:p-8 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-studio-border pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-studio-gold/15 border border-studio-gold/30 text-studio-gold">
              <Mic className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-studio-text">
                Live Voice Recorder
              </h3>
              <p className="text-xs text-studio-muted">
                Record 5 to 60 seconds for zero-shot voice cloning
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              resetAll();
              onClose();
            }}
            className="p-1.5 rounded-lg text-studio-muted hover:text-studio-text hover:bg-studio-surface transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-studio-rose/10 border border-studio-rose/30 flex items-start gap-2.5 text-xs text-studio-rose">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Recording Interface */}
        {(state === "idle" || state === "recording" || state === "paused") && (
          <div className="flex flex-col items-center justify-center py-6 space-y-5">
            {/* Visualizer Canvas */}
            <div className="w-full h-16 bg-studio-surface border border-studio-border rounded-2xl flex items-center justify-center overflow-hidden px-4">
              {state === "recording" || state === "paused" ? (
                <canvas
                  ref={canvasRef}
                  width={380}
                  height={60}
                  className="w-full h-full"
                />
              ) : (
                <span className="text-xs text-studio-muted flex items-center gap-2">
                  <Volume2 className="w-4 h-4 text-studio-gold" />
                  Ready to capture audio stream (16kHz Mono)
                </span>
              )}
            </div>

            {/* Timer */}
            <div className="flex items-center gap-2">
              {state === "recording" && (
                <span className="w-2.5 h-2.5 rounded-full bg-studio-rose animate-ping" />
              )}
              <span className="text-2xl font-mono font-bold text-studio-text tracking-wider">
                {formatTimer(duration)}
              </span>
              <span className="text-xs text-studio-muted">/ 01:00</span>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4">
              {state === "idle" && (
                <button
                  type="button"
                  onClick={startRecording}
                  className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-studio-gold to-studio-amber text-studio-bg font-bold text-sm shadow-gold hover:opacity-95 transition-all flex items-center gap-2.5 cursor-pointer"
                >
                  <Mic className="w-5 h-5" />
                  <span>Start Recording</span>
                </button>
              )}

              {state === "recording" && (
                <>
                  <button
                    type="button"
                    onClick={pauseRecording}
                    className="p-3.5 rounded-2xl bg-studio-surface border border-studio-border hover:border-studio-gold text-studio-text hover:text-studio-gold transition-colors cursor-pointer"
                    title="Pause"
                  >
                    <Pause className="w-5 h-5" />
                  </button>
                  <button
                    type="button"
                    onClick={stopRecording}
                    className="px-6 py-3.5 rounded-2xl bg-studio-rose text-white font-bold text-sm shadow-lg hover:opacity-95 transition-all flex items-center gap-2 cursor-pointer"
                  >
                    <Square className="w-4 h-4 fill-current" />
                    <span>Stop Recording</span>
                  </button>
                </>
              )}

              {state === "paused" && (
                <>
                  <button
                    type="button"
                    onClick={resumeRecording}
                    className="p-3.5 rounded-2xl bg-studio-gold text-studio-bg font-bold shadow-gold hover:opacity-95 transition-all cursor-pointer"
                    title="Resume"
                  >
                    <Play className="w-5 h-5 fill-current" />
                  </button>
                  <button
                    type="button"
                    onClick={stopRecording}
                    className="px-6 py-3.5 rounded-2xl bg-studio-rose text-white font-bold text-sm shadow-lg hover:opacity-95 transition-all flex items-center gap-2 cursor-pointer"
                  >
                    <Square className="w-4 h-4 fill-current" />
                    <span>Finish</span>
                  </button>
                </>
              )}
            </div>

            <p className="text-[11px] text-studio-muted text-center max-w-xs">
              Recite clean Urdu poetry or speech clearly into your microphone.
            </p>
          </div>
        )}

        {/* Stopped / Review & Enhancement Panel */}
        {state === "stopped" && (
          <div className="space-y-5">
            {/* Audio Playback Player */}
            <div className="p-4 rounded-2xl bg-studio-surface border border-studio-border flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={togglePlayback}
                  className="w-10 h-10 rounded-xl bg-studio-gold text-studio-bg flex items-center justify-center font-bold shadow-gold cursor-pointer hover:opacity-95"
                >
                  {isPlaying ? (
                    <Pause className="w-5 h-5 fill-current" />
                  ) : (
                    <Play className="w-5 h-5 fill-current ml-0.5" />
                  )}
                </button>
                <div>
                  <div className="text-xs font-bold text-studio-text">
                    Recorded Audio Preview
                  </div>
                  <div className="text-[11px] text-studio-muted font-mono">
                    Duration: {formatTimer(duration)} • 16 kHz Mono WAV
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={resetAll}
                className="text-xs text-studio-muted hover:text-studio-rose flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retake</span>
              </button>

              {processedAudioUrl && (
                <audio
                  ref={audioPlayerRef}
                  src={processedAudioUrl}
                  onEnded={() => setIsPlaying(false)}
                  className="hidden"
                />
              )}
            </div>

            {/* Voice Enhancement Options */}
            <div className="p-4 rounded-2xl bg-studio-surface/60 border border-studio-border space-y-4">
              <div className="flex items-center justify-between text-xs font-bold text-studio-gold uppercase tracking-wider">
                <span className="flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  Voice Enhancement Options
                </span>
                {isEnhancing && (
                  <span className="text-[10px] text-studio-muted font-normal animate-pulse">
                    Processing...
                  </span>
                )}
              </div>

              {/* Toggles */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <label className="flex items-center justify-between p-2.5 rounded-xl bg-studio-card border border-studio-border cursor-pointer">
                  <span className="text-studio-text">Noise Reduction</span>
                  <input
                    type="checkbox"
                    checked={noiseReduction}
                    onChange={(e) => {
                      setNoiseReduction(e.target.checked);
                      enhanceAudio(audioBuffer, e.target.checked, normalizeVolume, eqPreset);
                    }}
                    className="accent-studio-gold w-4 h-4 cursor-pointer"
                  />
                </label>

                <label className="flex items-center justify-between p-2.5 rounded-xl bg-studio-card border border-studio-border cursor-pointer">
                  <span className="text-studio-text">Volume Normalization</span>
                  <input
                    type="checkbox"
                    checked={normalizeVolume}
                    onChange={(e) => {
                      setNormalizeVolume(e.target.checked);
                      enhanceAudio(audioBuffer, noiseReduction, e.target.checked, eqPreset);
                    }}
                    className="accent-studio-gold w-4 h-4 cursor-pointer"
                  />
                </label>
              </div>

              {/* EQ Presets */}
              <div>
                <label className="block text-[11px] font-semibold text-studio-muted uppercase tracking-wider mb-2">
                  EQ Preset
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {(
                    [
                      { id: "none", label: "Natural" },
                      { id: "warm", label: "Warm" },
                      { id: "clear", label: "Clear" },
                      { id: "deep", label: "Deep" },
                    ] as const
                  ).map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        setEqPreset(item.id);
                        enhanceAudio(audioBuffer, noiseReduction, normalizeVolume, item.id);
                      }}
                      className={`py-1.5 text-xs rounded-lg border font-medium transition-colors cursor-pointer ${
                        eqPreset === item.id
                          ? "bg-studio-gold/20 border-studio-gold text-studio-gold font-bold"
                          : "bg-studio-card border-studio-border text-studio-muted hover:text-studio-text"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  resetAll();
                  onClose();
                }}
                className="px-4 py-2.5 rounded-xl border border-studio-border text-xs text-studio-muted hover:text-studio-text transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUseRecording}
                disabled={!processedBlob || isEnhancing}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-studio-gold to-studio-amber text-studio-bg font-bold text-xs shadow-gold hover:opacity-95 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Use This Voice Profile</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// 16-bit PCM WAV Encoder helper
function encodeWavBlob(channelData: Float32Array, sampleRate: number): Blob {
  const numChannels = 1;
  const bitDepth = 16;
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;
  const numSamples = channelData.length;
  const dataByteCount = numSamples * bytesPerSample;
  const wavBuffer = new ArrayBuffer(44 + dataByteCount);
  const view = new DataView(wavBuffer);

  const writeString = (v: DataView, offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      v.setUint8(offset + i, str.charCodeAt(i));
    }
  };

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + dataByteCount, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  writeString(view, 36, "data");
  view.setUint32(40, dataByteCount, true);

  let offset = 44;
  for (let i = 0; i < numSamples; i++) {
    const s = Math.max(-1, Math.min(1, channelData[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    offset += 2;
  }

  return new Blob([wavBuffer], { type: "audio/wav" });
}

