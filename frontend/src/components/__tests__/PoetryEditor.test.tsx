import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { PoetryEditor } from "../PoetryEditor";

describe("PoetryEditor Component", () => {
  it("renders editor fields and metrics correctly", () => {
    const mockChangeText = vi.fn();
    const mockChangeTitle = vi.fn();
    const mockChangePoet = vi.fn();

    render(
      <PoetryEditor
        poetryText={"دل ناداں تجھے ہوا کیا ہے\nآخر اس درد کی دوا کیا ہے"}
        onChangeText={mockChangeText}
        title="دل ناداں"
        onChangeTitle={mockChangeTitle}
        poetName="مرزا غالب"
        onChangePoetName={mockChangePoet}
      />
    );

    expect(screen.getByDisplayValue("دل ناداں")).toBeDefined();
    expect(screen.getByDisplayValue("مرزا غالب")).toBeDefined();
    expect(
      screen.getByDisplayValue(/دل ناداں تجھے ہوا کیا ہے/)
    ).toBeDefined();

    // Verify verse count
    expect(screen.getByText("Verses:")).toBeDefined();
  });

  it("inserts diacritics when aerab buttons are clicked", () => {
    const mockChangeText = vi.fn();
    render(
      <PoetryEditor
        poetryText="دل"
        onChangeText={mockChangeText}
        title=""
        onChangeTitle={vi.fn()}
        poetName=""
        onChangePoetName={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText(/یہاں اپنا اردو کلام/) as HTMLTextAreaElement;
    textarea.focus();
    textarea.setSelectionRange(2, 2);

    const zabarBtn = screen.getByTitle("زبر");
    fireEvent.click(zabarBtn);

    expect(mockChangeText).toHaveBeenCalledWith("دل\u064E");
  });

  it("loads a preset when clicked", () => {
    const mockChangeText = vi.fn();
    const mockChangeTitle = vi.fn();
    const mockChangePoet = vi.fn();

    render(
      <PoetryEditor
        poetryText=""
        onChangeText={mockChangeText}
        title=""
        onChangeTitle={mockChangeTitle}
        poetName=""
        onChangePoetName={mockChangePoet}
      />
    );

    const ghalibBtn = screen.getByText("مرزا غالب");
    fireEvent.click(ghalibBtn);

    expect(mockChangeTitle).toHaveBeenCalledWith("دل ناداں");
    expect(mockChangePoet).toHaveBeenCalledWith("مرزا غالب");
    expect(mockChangeText).toHaveBeenCalledWith(
      "دل ناداں تجھے ہوا کیا ہے\nآخر اس درد کی دوا کیا ہے"
    );
  });
});
