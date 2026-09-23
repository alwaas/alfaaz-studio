# AlfaazStudio (الفاظ اسٹوڈیو) 🎙️✨

> **Local-first Urdu Poetry AI Voice-over Studio for 9:16 Instagram Reels & Shorts**

[![Tests](https://img.shields.io/badge/Backend%20Tests-95%2F95%20Passing-success)](#testing)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-18%2F18%20Passing-success)](#testing)
[![Coverage](https://img.shields.io/badge/Code%20Coverage-81%25-brightgreen)](#testing)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](#tech-stack)
[![Next.js](https://img.shields.io/badge/Next.js-14.2%20App%20Router-black)](#tech-stack)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)](#tech-stack)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20CC--BY--NC--4.0-orange)](#licensing--compliance)

---

## 📖 Overview

**AlfaazStudio** is an autonomous studio designed for creators, poets, and video editors to transform classical and contemporary Urdu poetry (Shayari) into atmospheric 9:16 vertical Instagram Reels.

With zero cloud dependencies, complete privacy, and authentic Nastaliq typography, AlfaazStudio generates expressive speech, applies warm tube acoustic mastering, dynamic background music ducking, and renders high-definition vertical video with kinetic word-by-word karaoke highlighting.

---

## 🌟 Key Features

1. **Urdu Text Processing & Aerab Engine**:
   - Comprehensive Urdu Unicode normalization (NFC, Arabic glyph transliteration).
   - Preserves classical Urdu punctuation (`۔`, `؟`, `!`, `،`).
   - Automatic verse (*Misra*) and couplet (*She'r*) segmentation.
   - Customizable pronunciation substitution dictionary for poetic meter (*Vazn*).

2. **Multi-Engine TTS & Zero-Shot Voice Cloning**:
   - **F5-TTS (Urdu DiT)**: Expressive zero-shot voice cloning with 5–15 second reference samples.
   - **Piper TTS**: Ultra-lightweight CPU fallback (< 50MB models) for instant synthesis.
   - **MeloTTS**: Multi-lingual prosody with adjustable cadence.
   - **MockTTS**: Synthetic deterministic sine engine with harmonic overtone synthesis for rapid CI/CD test automation.

3. **Studio Acoustic DSP Mastering**:
   - **Warm Tube Parametric EQ**: Second-order Biquad peaking filter with low-end warmth (+3 dB at 200 Hz, Q=1.0) and high-end air (+2 dB at 10 kHz).
   - **Schroeder Algorithmic Reverb**: 4 parallel feedback comb filters + 2 series allpass diffusers creating a lush mushaira recital hall ambiance.
   - **Dynamic Compressor**: Soft-knee peak compressor with automatic makeup gain.
   - **Intelligent BGM Ducking**: Smooth envelope follower that automatically ducks background music beneath spoken verses by -14 dB.

4. **Authentic Nastaliq Typography & Kinetic Subtitles**:
   - Advanced **ASS (Advanced SubStation Alpha)** subtitle script engine tailored for 1080×1920 vertical canvas.
   - Right-to-Left (RTL) text shaping with `Noto Nastaliq Urdu` and `Jameel Noori Nastaleeq`.
   - Word-level synchronization with kinetic karaoke highlight tags (`\k<duration>`).
   - Soft fade transitions (`\fad(200, 200)`), custom color grading, and drop shadows.

5. **FFmpeg 9:16 Vertical Video Render Engine**:
   - Cross-platform Windows/macOS/Linux path escaping for FFmpeg filters.
   - Procedural aesthetic themes:
     - 🌟 **Velvet & Gold**: Deep burgundy background with luminous gold calligraphy.
     - 🌲 **Mughal Emerald**: Imperial forest green with mint and champagne highlights.
     - 🕯️ **Candlelight Amber**: Warm umber and sepia reminiscent of candlelight Mehfils.
     - 🌧️ **Noir Rain**: High-contrast monochrome charcoal with silver metallic luster.
   - Fast H.264 video encoding with AAC stereo audio and `+faststart` MP4 metadata for mobile streaming.

6. **Modern Dark-Themed Next.js Web Studio**:
   - Step 1: **Poetry & Voice Selection** (Urdu Nastaliq editor, diacritics toolbar, voice profile selector).
   - Step 2: **Audio Editor & DSP** (Interactive Wavesurfer waveform, EQ warmth/air sliders, reverb room size, ducking controls).
   - Step 3: **Reel Preview & Export** (Realistic smartphone bezel preview frame, live Nastaliq layout simulation, theme cards, MP4 download).

---

## 🏗️ Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          Next.js 14 Web Frontend             │
                  │   (Poetry Editor, Waveform DSP, 9:16 Mockup) │
                  └───────────────────────┬──────────────────────┘
                                          │ HTTP REST API
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │             FastAPI 0.110 Backend            │
                  │    (Auth, System, Voices, Projects, Jobs)    │
                  └──────┬────────────────┬───────────────┬──────┘
                         │                │               │
                         ▼                ▼               ▼
                 ┌──────────────┐ ┌───────────────┐ ┌────────────┐
                 │  Urdu Utils  │ │ Audio DSP     │ │  ASS Sub-  │
                 │(Normalization│ │  Mastering    │ │   titles   │
                 │   & Aerab)   │ │(EQ/Reverb/Duck│ │ (Nastaliq) │
                 └──────┬───────┘ └───────┬───────┘ └─────┬──────┘
                        │                 │               │
                        ▼                 ▼               ▼
                 ┌──────────────┐ ┌───────────────┐ ┌────────────┐
                 │ TTS Engines  │ │ Audio Asset   │ │ FFmpeg     │
                 │(F5/Piper/    │ │ Storage       │ │ 9:16 Video │
                 │ Melo/Mock)   │ │ (Local-first) │ │ Engine     │
                 └──────────────┘ └───────────────┘ └─────┬──────┘
                                                          │
                                                          ▼
                                             1080x1920 MP4 Video Reel
```

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for Production)

Run the full studio with Redis, Celery workers, FastAPI backend, and Next.js frontend in isolated containers:

```bash
# Clone the repository
git clone https://github.com/alwaas/alfaaz-studio.git
cd alfaaz-studio

# Start all services
docker compose up --build
```

- **Frontend Studio UI**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Option 2: Local Development Setup

#### Prerequisites
- **Python**: 3.11+
- **UV**: Astral UV package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Node.js**: v20+ or v22+
- **FFmpeg**: With `libass` and `libx264` enabled

#### 1. Backend Setup

```bash
# Initialize Python environment
uv venv
uv pip install -r backend/requirements.txt

# Run database migrations
uv run alembic -c backend/alembic.ini upgrade head

# Launch FastAPI development server
uv run uvicorn app.main:app --app-dir backend --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view AlfaazStudio.

---

### Option 3: Headless Sample Reel Generator

Generate a sample 9:16 Mirza Ghalib poetry reel with DSP mastering and kinetic subtitles directly from the command line:

```bash
uv run python scripts/generate_sample_reel.py
```

The output will be saved to: `outputs/sample_ghalib_reel.mp4`.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | System health check and uptime |
| `GET` | `/api/v1/ready` | Readiness probe (database and storage connectivity) |
| `GET` | `/api/v1/system/device` | GPU / CPU acceleration status and VRAM metrics |
| `GET` | `/api/v1/system/model` | Loaded TTS model details and runtime status |
| `GET` | `/api/v1/system/storage` | Local storage disk usage and quotas |
| `POST` | `/api/v1/voices` | Create voice profile or upload cloning reference |
| `GET` | `/api/v1/voices` | List available voice profiles |
| `GET` | `/api/v1/voices/{id}` | Get voice profile details |
| `DELETE` | `/api/v1/voices/{id}` | Delete voice profile |
| `POST` | `/api/v1/projects` | Create a new poetry reel project |
| `GET` | `/api/v1/projects` | List projects with associated audio and video assets |
| `GET` | `/api/v1/projects/{id}` | Get project detail tree |
| `POST` | `/api/v1/projects/{id}/generate-audio` | Trigger async TTS speech synthesis |
| `GET` | `/api/v1/jobs/{id}` | Poll background task status and progress |
| `POST` | `/api/v1/jobs/{id}/cancel` | Cancel in-flight background task |
| `GET` | `/api/v1/audio/bgm/presets` | List background music mood tracks |
| `GET` | `/api/v1/audio/assets/{id}/stream` | Stream WAV/MP3 audio asset |
| `POST` | `/api/v1/audio/master` | Apply DSP mastering chain (EQ, Reverb, Ducking) |
| `POST` | `/api/v1/audio/trim-silence` | Trim silence from audio boundaries |
| `GET` | `/api/v1/rendering/themes` | List 9:16 aesthetic visual themes |
| `POST` | `/api/v1/rendering/render` | Render vertical MP4 video with ASS subtitles |
| `GET` | `/api/v1/rendering/videos/{id}/stream`| Stream rendered MP4 video |
| `GET` | `/api/v1/rendering/videos/{id}/download`| Download MP4 file for Instagram Reels |

---

## 🧪 Testing

AlfaazStudio follows strict quality gates with autonomous self-review under RALF MODE:

```bash
# Run all backend tests with coverage report
uv run pytest backend/tests --cov=backend/app --cov-report=term-missing

# Run frontend tests
cd frontend && npm test

# Run Next.js production build verification
cd frontend && npm run build

# Run RALF Mode Phase Validator
uv run python scripts/ralf_validator.py --phase 8
```

### Test Results
- **Backend Tests**: 95/95 passed (81% code coverage)
- **Frontend Tests**: 18/18 passed across 5 component and service suites
- **Next.js Production Build**: 0 type errors, 0 lint errors, optimized standalone bundle

---

## ⚖️ Licensing & Compliance

- **AlfaazStudio Codebase**: Licensed under the MIT License.
- **F5-TTS Voice Cloning Model**: Licensed under **Creative Commons Attribution Non-Commercial 4.0 (CC-BY-NC-4.0)**. Use of F5-TTS weights is strictly limited to personal and research use.
- **Piper TTS**: Mozilla Public License 2.0 (MPL-2.0) / MIT.
- **Urdu Fonts**: Noto Nastaliq Urdu is licensed under the SIL Open Font License (OFL-1.1).
- For complete licensing guidelines, see [MODEL_LICENSES.md](MODEL_LICENSES.md) and [PRIVACY.md](PRIVACY.md).

---

*Crafted with passion for Urdu Adab (اردو ادب) & Poetry Creators.* 📜🌙

