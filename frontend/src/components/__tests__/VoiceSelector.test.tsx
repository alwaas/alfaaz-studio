import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { VoiceSelector } from "../VoiceSelector";

describe("VoiceSelector Component", () => {
  it("renders all TTS engines and allows selecting an engine", () => {
    const mockChangeEngine = vi.fn();
    render(
      <VoiceSelector
        engine="f5-tts"
        onChangeEngine={mockChangeEngine}
        speed={1.0}
        onChangeSpeed={vi.fn()}
        pitch={0.0}
        onChangePitch={vi.fn()}
        speaker="ur-poet-male"
        onChangeSpeaker={vi.fn()}
        referenceFile={null}
        onSelectReferenceFile={vi.fn()}
      />
    );

    expect(screen.getByText("F5-TTS")).toBeDefined();
    expect(screen.getByText("MeloTTS")).toBeDefined();
    expect(screen.getByText("Piper TTS")).toBeDefined();

    // Verify F5-TTS personal use notice
    expect(screen.getByText(/Personal Use License/)).toBeDefined();

    // Switch to MeloTTS
    const meloBtn = screen.getByText("MeloTTS");
    fireEvent.click(meloBtn);
    expect(mockChangeEngine).toHaveBeenCalledWith("melotts");
  });

  it("handles speed slider updates", () => {
    const mockChangeSpeed = vi.fn();
    render(
      <VoiceSelector
        engine="piper"
        onChangeEngine={vi.fn()}
        speed={1.0}
        onChangeSpeed={mockChangeSpeed}
        pitch={0.0}
        onChangePitch={vi.fn()}
        speaker="ur-default"
        referenceFile={null}
        onSelectReferenceFile={vi.fn()}
      />
    );

    const speedSlider = screen.getAllByRole("slider")[0];
    fireEvent.change(speedSlider, { target: { value: "1.25" } });
    expect(mockChangeSpeed).toHaveBeenCalledWith(1.25);
  });
});

