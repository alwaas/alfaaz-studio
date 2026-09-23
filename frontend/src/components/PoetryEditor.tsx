"use client";

import { useRef } from "react";
import { BookOpen, Sparkles, Trash2, AlignRight } from "lucide-react";
import { PoetryPreset } from "@/types";

interface PoetryEditorProps {
  poetryText: string;
  onChangeText: (text: string) => void;
  title: string;
  onChangeTitle: (title: string) => void;
  poetName: string;
  onChangePoetName: (name: string) => void;
}

const POETRY_PRESETS: PoetryPreset[] = [
  {
    id: "ghalib-1",
    title: "دل ناداں",
    poet: "مرزا غالب",
    lines: [
      "دل ناداں تجھے ہوا کیا ہے",
      "آخر اس درد کی دوا کیا ہے",
    ],
  },
  {
    id: "iqbal-1",
    title: "ستاروں سے آگے",
    poet: "علامہ اقبال",
    lines: [
      "ستاروں سے آگے جہاں اور بھی ہیں",
      "ابھی عشق کے امتحان اور بھی ہیں",
    ],
  },
  {
    id: "faiz-1",
    title: "گلوں میں رنگ بھرے",
    poet: "فیض احمد فیض",
    lines: [
      "گلوں میں رنگ بھرے باد نوبہار چلے",
      "چلے بھی آؤ کہ گلشن کا کاروبار چلے",
    ],
  },
  {
    id: "faraz-1",
    title: "سنا ہے لوگ اسے",
    poet: "احمد فراز",
    lines: [
      "سنا ہے لوگ اسے آنکھ بھر کے دیکھتے ہیں",
      "سو اس کے شہر میں کچھ دن ٹھہر کے دیکھتے ہیں",
    ],
  },
];

const URDU_DIACRITICS = [
  { label: "زبر", char: "\u064E", preview: "ـَ" },
  { label: "زیر", char: "\u0650", preview: "ـِ" },
  { label: "پیش", char: "\u064F", preview: "ـُ" },
  { label: "تشدید", char: "\u0651", preview: "ـّ" },
  { label: "جزم", char: "\u0652", preview: "ـْ" },
  { label: "تنوین", char: "\u064B", preview: "ـً" },
  { label: "کھڑی زبر", char: "\u0670", preview: "ـٰ" },
  { label: "ہمزہ", char: "\u0621", preview: "ء" },
  { label: "ختمہ", char: "\u06D4", preview: "۔" },
  { label: "سکتہ", char: "\u060C", preview: "،" },
];

export function PoetryEditor({
  poetryText,
  onChangeText,
  title,
  onChangeTitle,
  poetName,
  onChangePoetName,
}: PoetryEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const insertDiacritic = (char: string) => {
    const el = textareaRef.current;
    if (!el) {
      onChangeText(poetryText + char);
      return;
    }

    let start = el.selectionStart ?? poetryText.length;
    let end = el.selectionEnd ?? poetryText.length;

    // If textarea lost focus and selection was reset to 0, append to end of text
    if (start === 0 && end === 0 && document.activeElement !== el) {
      start = poetryText.length;
      end = poetryText.length;
    }

    const updated = poetryText.substring(0, start) + char + poetryText.substring(end);
    onChangeText(updated);

    // Restore cursor position after the inserted character
    setTimeout(() => {
      el.focus();
      el.setSelectionRange(start + char.length, start + char.length);
    }, 0);
  };

  const loadPreset = (preset: PoetryPreset) => {
    onChangeTitle(preset.title);
    onChangePoetName(preset.poet);
    onChangeText(preset.lines.join("\n"));
  };

  // Compute metrics
  const lines = poetryText.split("\n").filter((l) => l.trim().length > 0);
  const words = poetryText.trim().split(/\s+/).filter((w) => w.length > 0);
  const coupletCount = Math.floor(lines.length / 2);

  return (
    <div className="bg-studio-card border border-studio-border rounded-2xl p-6 shadow-studio">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-studio-border">
        <div className="flex items-center gap-2.5">
          <BookOpen className="w-5 h-5 text-studio-gold" />
          <h2 className="text-base font-semibold text-studio-text">
            Urdu Poetry Stanza
          </h2>
        </div>

        {/* Presets Picker */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-studio-muted">Preset:</span>
          {POETRY_PRESETS.map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => loadPreset(preset)}
              className="px-2.5 py-1 text-xs rounded-lg bg-studio-surface border border-studio-border hover:border-studio-gold/60 text-studio-text hover:text-studio-gold transition-colors font-nastaliq"
            >
              {preset.poet}
            </button>
          ))}
        </div>
      </div>

      {/* Meta Fields: Title & Poet */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-4">
        <div>
          <label className="block text-xs font-medium text-studio-muted mb-1.5">
            Project Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => onChangeTitle(e.target.value)}
            placeholder="e.g., Dil-e-Nadaan"
            className="w-full px-3.5 py-2 rounded-xl bg-studio-surface border border-studio-border text-sm text-studio-text focus:outline-none focus:border-studio-gold transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-studio-muted mb-1.5">
            Poet Name
          </label>
          <input
            type="text"
            value={poetName}
            onChange={(e) => onChangePoetName(e.target.value)}
            placeholder="e.g., Mirza Ghalib"
            className="w-full px-3.5 py-2 rounded-xl bg-studio-surface border border-studio-border text-sm text-studio-text focus:outline-none focus:border-studio-gold transition-colors"
          />
        </div>
      </div>

      {/* Diacritics (Aerab) Toolbar */}
      <div className="mb-3 p-2 rounded-xl bg-studio-surface border border-studio-border/60 flex items-center gap-1.5 overflow-x-auto">
        <span className="text-[11px] font-medium text-studio-muted px-2 shrink-0">
          Aerab (Diacritics):
        </span>
        {URDU_DIACRITICS.map((item) => (
          <button
            key={item.label}
            type="button"
            onClick={() => insertDiacritic(item.char)}
            className="px-2.5 py-1 rounded-lg bg-studio-card hover:bg-studio-hover border border-studio-border text-sm font-nastaliq text-studio-gold hover:text-white transition-colors shrink-0"
            title={item.label}
          >
            {item.preview}
          </button>
        ))}
      </div>

      {/* Nastaliq Poetry Textarea */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={poetryText}
          onChange={(e) => onChangeText(e.target.value)}
          rows={6}
          dir="rtl"
          placeholder="یہاں اپنا اردو کلام یا شعر درج کریں..."
          className="w-full p-4 rounded-xl bg-studio-surface border border-studio-border focus:border-studio-gold text-studio-text urdu-text text-xl focus:outline-none transition-colors resize-none placeholder:text-studio-muted/40"
        />

        {poetryText && (
          <button
            type="button"
            onClick={() => onChangeText("")}
            className="absolute top-3 left-3 p-1.5 rounded-lg bg-studio-card/80 hover:bg-studio-rose/20 text-studio-muted hover:text-studio-rose transition-colors"
            title="Clear text"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Footer Metrics */}
      <div className="mt-4 pt-3 border-t border-studio-border flex items-center justify-between text-xs text-studio-muted">
        <div className="flex items-center gap-4">
          <span>
            Verses:{" "}
            <strong className="text-studio-text font-semibold">
              {lines.length}
            </strong>
          </span>
          <span>
            Couplets:{" "}
            <strong className="text-studio-text font-semibold">
              {coupletCount}
            </strong>
          </span>
          <span>
            Words:{" "}
            <strong className="text-studio-text font-semibold">
              {words.length}
            </strong>
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-studio-gold/80">
          <AlignRight className="w-3.5 h-3.5" />
          <span>Nastaliq RTL Active</span>
        </div>
      </div>
    </div>
  );
}

