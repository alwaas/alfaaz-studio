import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { VoiceRecorder } from "../VoiceRecorder";

describe("VoiceRecorder Component", () => {
  const mockOnClose = vi.fn();
  const mockOnSave = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("does not render when isOpen is false", () => {
    const { container } = render(
      <VoiceRecorder
        isOpen={false}
        onClose={mockOnClose}
        onSaveRecording={mockOnSave}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders recorder modal with controls when isOpen is true", () => {
    render(
      <VoiceRecorder
        isOpen={true}
        onClose={mockOnClose}
        onSaveRecording={mockOnSave}
      />
    );

    expect(screen.getByText("Live Voice Recorder")).toBeDefined();
    expect(
      screen.getByText("Record 5 to 60 seconds for zero-shot voice cloning")
    ).toBeDefined();
    expect(screen.getByText("Start Recording")).toBeDefined();
    expect(screen.getByText("00:00")).toBeDefined();
  });

  it("invokes onClose when close button is clicked", () => {
    render(
      <VoiceRecorder
        isOpen={true}
        onClose={mockOnClose}
        onSaveRecording={mockOnSave}
      />
    );

    const closeBtn = screen.getByRole("button", { name: "" }); // X button
    fireEvent.click(closeBtn);
    expect(mockOnClose).toHaveBeenCalled();
  });
});
