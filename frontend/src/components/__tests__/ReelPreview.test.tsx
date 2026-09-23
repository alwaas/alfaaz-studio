import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { ReelPreview } from "../ReelPreview";
import { api } from "@/services/api";

// Mock api methods
vi.mock("@/services/api", () => ({
  api: {
    getReelThemes: vi.fn().mockResolvedValue([
      {
        id: "velvet-gold",
        name: "Velvet & Gold",
        description: "Midnight navy with royal gold",
        bg_color_hex: "0x080B14",
        accent_color_hex: "0xF59E0B",
      },
      {
        id: "emerald-night",
        name: "Mughal Emerald",
        description: "Jade-emerald atmosphere",
        bg_color_hex: "0x06140E",
        accent_color_hex: "0x10B981",
      },
    ]),
    renderReel: vi.fn().mockResolvedValue({
      video_asset_id: "video-123",
      project_id: "proj-1",
      filename: "reel_test.mp4",
      duration: 10.0,
      resolution: "1080x1920",
      fps: 30,
      stream_url: "/api/v1/rendering/videos/video-123/stream",
      download_url: "/api/v1/rendering/videos/video-123/download",
      status: "rendered",
    }),
    getVideoStreamUrl: vi.fn((id: string) => `/api/v1/rendering/videos/${id}/stream`),
    getVideoDownloadUrl: vi.fn((id: string) => `/api/v1/rendering/videos/${id}/download`),
  },
}));

describe("ReelPreview Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders 9:16 vertical smartphone preview frame and themes", async () => {
    render(
      <ReelPreview
        projectId="proj-1"
        audioAssetId="audio-1"
        title="دیوان غالب"
        poetName="مرزا غالب"
        poetryVerses={["دل ناداں تجھے ہوا کیا ہے", "آخر اس درد کی دوا کیا ہے"]}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Aesthetic Visual Theme")).toBeDefined();
    });

    expect(screen.getByText("1080x1920 Vertical Feed Preview")).toBeDefined();
    expect(screen.getByText("دیوان غالب")).toBeDefined();
    expect(screen.getAllByText(/مرزا غالب/).length).toBeGreaterThan(0);
    expect(screen.getByText(/دل ناداں تجھے ہوا کیا ہے/)).toBeDefined();
    expect(screen.getByText("Nastaliq Subtitle Typography")).toBeDefined();
  });

  it("selects a theme when clicked", async () => {
    render(
      <ReelPreview
        projectId="proj-1"
        audioAssetId="audio-1"
        title="دیوان غالب"
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Velvet & Gold")).toBeDefined();
    });

    const emeraldBtn = screen.getByText("Mughal Emerald");
    fireEvent.click(emeraldBtn);
    expect(emeraldBtn).toBeDefined();
  });

  it("adjusts calligraphy font size slider", async () => {
    render(
      <ReelPreview
        projectId="proj-1"
        audioAssetId="audio-1"
        title="دیوان غالب"
      />
    );

    await waitFor(() => {
      expect(screen.getByText("60 pt")).toBeDefined();
    });

    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: "72" } });
    expect(screen.getByText("72 pt")).toBeDefined();
  });

  it("triggers reel rendering and invokes onRenderComplete", async () => {
    const mockComplete = vi.fn();

    render(
      <ReelPreview
        projectId="proj-1"
        audioAssetId="audio-1"
        title="دیوان غالب"
        onRenderComplete={mockComplete}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Render 9:16 Vertical Reel (MP4)")).toBeDefined();
    });

    const renderBtn = screen.getByText("Render 9:16 Vertical Reel (MP4)");
    fireEvent.click(renderBtn);

    await waitFor(() => {
      expect(api.renderReel).toHaveBeenCalledWith(
        expect.objectContaining({
          project_id: "proj-1",
          audio_asset_id: "audio-1",
          theme_id: "velvet-gold",
        })
      );
    });

    await waitFor(() => {
      expect(mockComplete).toHaveBeenCalledWith(
        "video-123",
        "/api/v1/rendering/videos/video-123/stream"
      );
    });

    // Check export button presence
    expect(screen.getByText("Export Reel (MP4)")).toBeDefined();
  });
});
