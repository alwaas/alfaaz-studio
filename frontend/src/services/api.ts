/**
 * Typed API Client for AlfaazStudio Backend Service.
 */

import {
  Job,
  Project,
  ProjectCreateInput,
  SystemDeviceTelemetry,
  VoiceProfile,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      // Non-JSON error body
    }
    throw new ApiError(res.status, errorDetail);
  }
  return res.json();
}

export const api = {
  // System Telemetry
  async getHealth(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  async getDeviceTelemetry(): Promise<SystemDeviceTelemetry> {
    const res = await fetch(`${API_BASE}/system/device`);
    return handleResponse(res);
  },

  async getModelTelemetry(): Promise<Record<string, any>> {
    const res = await fetch(`${API_BASE}/system/model`);
    return handleResponse(res);
  },

  // Voices CRUD
  async listVoices(): Promise<VoiceProfile[]> {
    const res = await fetch(`${API_BASE}/voices`);
    return handleResponse(res);
  },

  async getVoice(id: string): Promise<VoiceProfile> {
    const res = await fetch(`${API_BASE}/voices/${id}`);
    return handleResponse(res);
  },

  async createVoice(formData: FormData): Promise<VoiceProfile> {
    const res = await fetch(`${API_BASE}/voices`, {
      method: "POST",
      body: formData,
    });
    return handleResponse(res);
  },

  async deleteVoice(id: string): Promise<{ success: boolean }> {
    const res = await fetch(`${API_BASE}/voices/${id}`, {
      method: "DELETE",
    });
    return handleResponse(res);
  },

  // Projects CRUD
  async listProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`);
    return handleResponse(res);
  },

  async getProject(id: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`);
    return handleResponse(res);
  },

  async createProject(input: ProjectCreateInput): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    return handleResponse(res);
  },

  async deleteProject(id: string): Promise<{ success: boolean }> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      method: "DELETE",
    });
    return handleResponse(res);
  },

  // Audio Synthesis & Queue Jobs
  async generateAudio(
    projectId: string,
    options: { speed?: number; voice_id?: string } = {}
  ): Promise<Job> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/generate-audio`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    });
    return handleResponse(res);
  },

  async getJob(id: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${id}`);
    return handleResponse(res);
  },

  async cancelJob(id: string): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/jobs/${id}/cancel`, {
      method: "POST",
    });
    return handleResponse(res);
  },

  async getJobLogs(id: string): Promise<{ job_id: string; logs: string[] }> {
    const res = await fetch(`${API_BASE}/jobs/${id}/logs`);
    return handleResponse(res);
  },
};

