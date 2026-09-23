import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { api } from "../api";

describe("Frontend API Client Service", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("fetches health status successfully", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "healthy" }),
    });

    const data = await api.getHealth();
    expect(data.status).toBe("healthy");
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining("/api/v1/health"));
  });

  it("fetches device hardware telemetry", async () => {
    const mockTelemetry = {
      device: "cuda",
      cpu_count: 8,
      cpu_percent: 22.5,
      ram_total_mb: 32768,
      ram_available_mb: 24000,
      cuda_available: true,
      gpu_name: "NVIDIA GeForce RTX 4090",
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTelemetry,
    });

    const data = await api.getDeviceTelemetry();
    expect(data.device).toBe("cuda");
    expect(data.gpu_name).toContain("RTX 4090");
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining("/api/v1/system/device"));
  });

  it("creates a new poetry project", async () => {
    const mockProject = {
      id: "proj-123",
      title: "گلوں میں رنگ بھرے",
      raw_poetry: "گلوں میں رنگ بھرے باد نوبہار چلے",
      status: "draft",
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockProject,
    });

    const created = await api.createProject({
      title: "گلوں میں رنگ بھرے",
      raw_poetry: "گلوں میں رنگ بھرے باد نوبہار چلے",
    });

    expect(created.id).toBe("proj-123");
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/projects"),
      expect.objectContaining({
        method: "POST",
      })
    );
  });

  it("handles HTTP errors with ApiError exception", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ detail: "Project not found" }),
    });

    await expect(api.getProject("invalid-id")).rejects.toThrow("Project not found");
  });
});

