/**
 * TypeScript Interface Definitions for AlfaazStudio Frontend.
 */

export interface VoiceProfile {
  id: string;
  name: string;
  engine: "f5-tts" | "melotts" | "piper" | "mock" | string;
  language: string;
  accent?: string | null;
  gender?: "male" | "female" | "neutral" | null;
  sample_rate: number;
  reference_audio_path?: string | null;
  is_default: boolean;
  created_at: string;
}

export interface AudioAsset {
  id: string;
  project_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  duration: number;
  sample_rate: number;
  channels: number;
  mime_type: string;
  asset_type: "raw_tts" | "bgm" | "mastered";
  created_at: string;
}

export interface VideoAsset {
  id: string;
  project_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  duration: number;
  width: number;
  height: number;
  fps: number;
  mime_type: string;
  created_at: string;
}

export interface Project {
  id: string;
  title: string;
  poet_name?: string | null;
  raw_poetry: string;
  normalized_poetry?: string | null;
  voice_id?: string | null;
  status: "draft" | "synthesizing" | "audio_ready" | "rendering" | "completed" | "failed";
  audio_assets: AudioAsset[];
  video_assets: VideoAsset[];
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateInput {
  title: string;
  raw_poetry: string;
  poet_name?: string;
  voice_id?: string;
}

export interface Job {
  id: string;
  job_type: "audio_generation" | "video_rendering" | "voice_cloning" | string;
  status: "pending" | "processing" | "completed" | "failed" | "cancelled";
  progress: number;
  error_message?: string | null;
  result?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface WordTimestamp {
  word: string;
  start_time: number;
  end_time: number;
  confidence?: number;
}

export interface SystemDeviceTelemetry {
  device: "cuda" | "cpu";
  cpu_count: number;
  cpu_percent: number;
  ram_total_mb: number;
  ram_available_mb: number;
  cuda_available: boolean;
  gpu_name?: string | null;
  vram_total_mb?: number | null;
  vram_free_mb?: number | null;
}

export interface AudioMasteringSettings {
  speed: number;
  pitch: number;
  warmth_db: number;
  air_db: number;
  reverb_wet: number;
  room_size: number;
  enable_compression: boolean;
  compressor_threshold_db: number;
  bgm_preset_id?: string | null;
  bgm_volume: number;
  ducking_depth_db: number;
}

export interface BGMPreset {
  id: string;
  name: string;
  category: string;
  description: string;
}

export interface AudioMasteringRequest {
  asset_id: string;
  speed?: number;
  pitch?: number;
  warmth_db?: number;
  air_db?: number;
  reverb_wet?: number;
  room_size?: number;
  enable_compression?: boolean;
  compressor_threshold_db?: number;
  bgm_preset_id?: string | null;
  bgm_volume?: number;
  ducking_depth_db?: number;
}

export interface AudioTrimRequest {
  asset_id: string;
  threshold_db?: number;
}

export interface AudioMasteringResponse {
  asset_id: string;
  project_id?: string | null;
  filename: string;
  duration: number;
  sample_rate: number;
  stream_url: string;
  status: string;
}

export interface PoetryPreset {
  id: string;
  title: string;
  poet: string;
  lines: string[];
}

export interface ReelThemePreset {
  id: string;
  name: string;
  description: string;
  bg_color_hex: string;
  accent_color_hex: string;
}

export interface ReelRenderRequest {
  project_id: string;
  audio_asset_id: string;
  theme_id?: string;
  bg_video_path?: string | null;
  font_name?: string;
  font_size?: number;
  enable_karaoke?: boolean;
  fps?: number;
}

export interface ReelRenderResponse {
  video_asset_id: string;
  project_id: string;
  filename: string;
  duration: number;
  resolution: string;
  fps: number;
  stream_url: string;
  download_url: string;
  status: string;
}

