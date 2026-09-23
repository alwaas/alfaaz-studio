# AlfaazStudio - Master Project Plan & Roadmap

## 1. Project Overview & Vision

AlfaazStudio (الفاظ اسٹوڈیو) is an automated studio environment designed for Urdu poets, creators, and literary enthusiasts to generate professional, viral-ready Instagram Reels and YouTube Shorts. It bridges cutting-edge open-source neural speech synthesis (F5-TTS, MeloTTS) with cinematic audio mastering and authentic Nastaliq calligraphy typography.

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2, PyTorch, Librosa, SoundFile, PyDub, SciPy |
| **Frontend** | Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, Wavesurfer.js, Lucide Icons |
| **Media Pipeline** | FFmpeg (with `libass`, `harfbuzz`, `fribidi`, `h264_nvenc`), ASS Subtitles |
| **Typography** | Jameel Noori Nastaleeq, Noto Nastaliq Urdu, Gulzar |
| **Infrastructure** | Docker, Docker Compose, UV package manager, Git |
| **Quality & CI** | Pytest, Pytest-Cov, Pytest-Asyncio, Ruff, Mypy, Vitest/Jest |

---

## 3. Phase Breakdown & Deliverables

### Phase 1: Architecture & Compliance (Current)
- **Objective**: Establish project foundations, directory taxonomy, licensing parameters, and architectural contracts.
- **Key Tasks**:
  - [x] Configure workspace directories (`backend`, `frontend`, `infra`, `models`, `outputs`, `temp`).
  - [x] Author comprehensive legal & compliance documentation (`MODEL_LICENSES.md`).
  - [x] Formulate high-level system architecture & diagrams (`ARCHITECTURE.md`).
  - [x] Draft local-first privacy policy (`PRIVACY.md`).
  - [x] Define master roadmap (`PROJECT_PLAN.md`).
  - [x] Initialize backend configuration (`requirements.txt`, `pyproject.toml`).
  - [x] Initialize frontend configuration (`package.json`, `tsconfig.json`).
  - [x] Supply environment template (`.env.example`).
- **Quality Gate**: 100% checks passed on `scripts/ralf_validator.py`.

### Phase 2: Backend Foundation
- **Objective**: Construct production-ready FastAPI service layer, health checks, settings, and test harness.
- **Key Tasks**:
  - Setup `backend/app/main.py`, `backend/app/config.py`.
  - Implement `/api/v1/health` with GPU/CPU hardware detection, memory status, and disk availability.
  - Implement CORS, global error handlers, and structured logging.
  - Establish unit tests with `pytest` achieving >= 80% coverage.
- **Quality Gate**: Backend test suite passing with >= 80% coverage.

### Phase 3: Mock TTS & Urdu Utils
- **Objective**: Develop core text processing for Urdu poetry and deterministic mock TTS audio synthesis.
- **Key Tasks**:
  - Build `UrduNormalizer` (diacritics, ligature normalization, verse parsing, punctuation handling).
  - Create `MockTTSEngine` generating synthetic harmonic speech tones and word-level timing markers.
  - Implement timestamped subtitle generator for Nastaliq calligraphy formatting.
  - Unit tests covering edge cases in Urdu text and audio synthesis.
- **Quality Gate**: Test suite passing with >= 80% coverage.

### Phase 4: Real Urdu TTS Integration
- **Objective**: Integrate neural speech models with GPU acceleration and robust CPU fallback.
- **Key Tasks**:
  - Implement `F5TTSEngine` adapter with support for voice reference cloning.
  - Implement `MeloTTSEngine` / `PiperTTSEngine` adapters for fast lightweight synthesis.
  - Model loader with caching, SHA-256 integrity verification, and automatic hardware selection.
  - Audio post-processing pipeline (Reverb, EQ, Compression, BGM ducking).
- **Quality Gate**: Successful audio generation across all adapters with automated fallback on CPU.

### Phase 5: Frontend Foundation
- **Objective**: Build responsive Next.js application shell with Urdu typography support.
- **Key Tasks**:
  - Setup Next.js App Router, Tailwind CSS dark studio theme.
  - Integrate Urdu web fonts (*Jameel Noori Nastaleeq*, *Noto Nastaliq Urdu*) with proper RTL styling.
  - Build API client services connecting to FastAPI backend.
  - Create poetry stanza input interface with diacritic support.
- **Quality Gate**: Frontend builds cleanly with zero TypeScript errors.

### Phase 6: Audio Editor
- **Objective**: Provide timeline and waveform manipulation in browser.
- **Key Tasks**:
  - Integrate Wavesurfer.js for interactive waveform scrubbing.
  - Stanza-by-stanza audio segmentation and silence trimming.
  - Audio parameter controls (Pitch, Speed, Reverb wet/dry, BGM mix ratio).
  - Multi-track audio preview.
- **Quality Gate**: Interactive UI components verified with unit tests.

### Phase 7: Reel Rendering
- **Objective**: Full 9:16 Instagram Reel video rendering with kinetic Nastaliq typography.
- **Key Tasks**:
  - ASS subtitle script builder with word highlighting and smooth entrance transitions.
  - FFmpeg rendering engine combining background video/image loop, mastered audio, and subtitles.
  - Video preview canvas in frontend.
  - Export management with download and format presets.
- **Quality Gate**: End-to-end rendering produces a valid 1080x1920 MP4 file.

### Phase 8: Production Hardening
- **Objective**: Containerization, comprehensive validation, and release readiness.
- **Key Tasks**:
  - Docker Compose orchestration for backend and frontend.
  - Full end-to-end automated integration tests.
  - Sample reel generation script to verify the entire pipeline headlessly.
  - Final documentation, user guide, and release tagging (`v0.1.0`).
- **Quality Gate**: 100% completion across all verification suites.

---

## 4. RALF Mode Governance & Quality Gates

AlfaazStudio utilizes RALF Mode (Reinforcement Learning from AI Feedback):
1. **Autonomous Loop**: Automatic execution of phase tasks, self-evaluation, and iterative error recovery (up to 5 iterations per phase).
2. **Quality Threshold**: A phase only qualifies as complete when the confidence score is >= 85%.
3. **Rollback Safety**: Any catastrophic failure after 5 attempts rolls back to the prior checkpoint and flags human intervention.
4. **Auditability**: Every phase transition is recorded in `PROGRESS.md` and committed with milestone git tags.
