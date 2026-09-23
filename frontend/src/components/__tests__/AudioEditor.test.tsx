import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { AudioEditor } from "../AudioEditor";
import { api } from "@/services/api";

// Mock api methods
vi.mock("@/services/api", () => ({
  api: {
    getBgmPresets: vi.fn().mockResolvedValue([
      {
        id: "rubab-meditative",
        name: "Rubab Meditative",
        category: "acoustic",
        description: "Test Rubab",
      },
    ]),
    masterAudio: vi.fn().mockResolvedValue({
      asset_id: "mastered-asset-123",
      project_id: "project-1",
      filename: "mastered.wav",
      duration: 12.5,
      sample_rate: 24000,
      stream_url: "/api/v1/audio/assets/mastered-asset-123/stream",
      status: "mastered",
    }),
    trimSilence: vi.fn().mockResolvedValue({
      asset_id: "trimmed-asset-456",
      project_id: "project-1",
      filename: "trimmed.wav",
      duration: 10.2,
      sample_rate: 24000,
      stream_url: "/api/v1/audio/assets/trimmed-asset-456/stream",
      status: "trimmed",
    }),
  },
}));

// Mock wavesurfer.js
vi.mock("wavesurfer.js", () => {
  return {
    default: {
      create: vi.fn(() => ({
        on: vi.fn(),
        playPause: vi.fn(),
        stop: vi.fn(),
        seekTo: vi.fn(),
        destroy: vi.fn(),
        getDuration: vi.fn(() => 15.0),
      })),
    },
  };
});

describe("AudioEditor Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders editor controls, title and poetry verses", async () => {
    render(
      <AudioEditor
        assetId="test-asset-1"
        initialAudioUrl="/api/v1/audio/assets/test-asset-1/stream"
        title="دل ناداں"
        poetName="مرزا غالب"
        poetryVerses={[
          "دل ناداں تجھے ہوا کیا ہے",
          "آخر اس درد کی دوا کیا ہے",
        ]}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Audio: دل ناداں/)).toBeDefined();
    });
    expect(screen.getByText("مرزا غالب")).toBeDefined();
    expect(screen.getByText(/دل ناداں تجھے ہوا کیا ہے/)).toBeDefined();
    expect(screen.getByText(/آخر اس درد کی دوا کیا ہے/)).toBeDefined();
    expect(screen.getByText("Parametric Equalization")).toBeDefined();
    expect(screen.getByText("Mushaira Hall Acoustic Space")).toBeDefined();
    expect(screen.getByText("Broadcast Vocal Compressor")).toBeDefined();
  });

  it("allows toggling playback and stopping", async () => {
    render(
      <AudioEditor
        assetId="test-asset-1"
        initialAudioUrl="/api/v1/audio/assets/test-asset-1/stream"
        poetryVerses={["شعر نمبر ایک"]}
      />
    );

    await waitFor(() => {
      expect(screen.getByLabelText("Play audio")).toBeDefined();
    });

    const playBtn = screen.getByLabelText("Play audio");
    fireEvent.click(playBtn);

    const stopBtn = screen.getByLabelText("Stop audio");
    expect(stopBtn).toBeDefined();
    fireEvent.click(stopBtn);
  });

  it("navigates to verse when stanza marker is clicked", async () => {
    render(
      <AudioEditor
        assetId="test-asset-1"
        initialAudioUrl="/api/v1/audio/assets/test-asset-1/stream"
        poetryVerses={["مصرع اول", "مصرع ثانی"]}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("مصرع اول")).toBeDefined();
    });

    const verse1Btn = screen.getByText("مصرع اول");
    fireEvent.click(verse1Btn);
    expect(verse1Btn).toBeDefined();
  });

  it("triggers DSP mastering and calls onMasteringComplete", async () => {
    const mockComplete = vi.fn();

    render(
      <AudioEditor
        assetId="test-asset-1"
        initialAudioUrl="/api/v1/audio/assets/test-asset-1/stream"
        onMasteringComplete={mockComplete}
      />
    );

    const masterBtn = screen.getByText("Apply DSP Mastering Chain");
    fireEvent.click(masterBtn);

    await waitFor(() => {
      expect(api.masterAudio).toHaveBeenCalledWith(
        expect.objectContaining({
          asset_id: "test-asset-1",
          warmth_db: 2.5,
          air_db: 1.5,
          reverb_wet: 0.15,
        })
      );
    });

    await waitFor(() => {
      expect(mockComplete).toHaveBeenCalledWith(
        "mastered-asset-123",
        "/api/v1/audio/assets/mastered-asset-123/stream"
      );
    });
  });

  it("triggers silence trimming on button click", async () => {
    const mockComplete = vi.fn();

    render(
      <AudioEditor
        assetId="test-asset-1"
        initialAudioUrl="/api/v1/audio/assets/test-asset-1/stream"
        onMasteringComplete={mockComplete}
      />
    );

    const trimBtn = screen.getByText("Trim Silence");
    fireEvent.click(trimBtn);

    await waitFor(() => {
      expect(api.trimSilence).toHaveBeenCalledWith(
        expect.objectContaining({
          asset_id: "test-asset-1",
        })
      );
    });

    await waitFor(() => {
      expect(mockComplete).toHaveBeenCalledWith(
        "trimmed-asset-456",
        "/api/v1/audio/assets/trimmed-asset-456/stream"
      );
    });
  });
});
