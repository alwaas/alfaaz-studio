# AlfaazStudio - Privacy & Data Governance Policy

**Effective Date**: September 2026  
**Status**: Active  
**Classification**: Local-First / Zero-Telemetry  

---

## 1. Core Commitment: 100% Local-First & Zero-Telemetry

AlfaazStudio is engineered with a strict **Local-First Privacy Architecture**. We believe that artistic creations—especially original poetry, spoken audio, and personal voice samples—belong exclusively to the creator.

- **No Remote Telemetry**: AlfaazStudio collects **zero** telemetry, usage metrics, tracking pixels, crash logs, or analytics.
- **No Third-Party Cloud Transmissions**: All speech synthesis, audio processing, font shaping, and video rendering are conducted directly on your local machine or self-hosted server.
- **No External API Keys Required**: The application runs completely decoupled from third-party proprietary AI APIs (such as OpenAI, ElevenLabs, or Google Cloud TTS).

---

## 2. Data Categories & Handling

### 2.1 User Poetry & Text Inputs
- **Storage**: Saved strictly to your local workspace or temporary SQLite project files.
- **Processing**: Processed entirely in-memory by the local Urdu text normalizer and local TTS models.
- **Transmission**: Never transmitted over the internet.

### 2.2 Audio Recordings & Voice Cloning References
- **Storage**: Voice cloning audio reference clips uploaded by the user are stored locally in the user's project directory or `temp/` folder.
- **Security**: Audio files are never uploaded to any cloud server or used to train public foundational AI models.
- **Deletion**: Users can delete their voice presets and samples at any time with immediate local effect.

### 2.3 Rendered Media (Outputs)
- **Destination**: Exported Instagram Reels and mastered WAV audio tracks are placed in the local `outputs/` directory.
- **Ownership**: The user retains full copyright and intellectual property rights over all generated media, subject to the open-source model licenses documented in [MODEL_LICENSES.md](MODEL_LICENSES.md).

---

## 3. Ephemeral File Management & Temporary Data

- During voice generation and video rendering, intermediate files (uncompressed PCM audio chunks, individual video frames, and `.ass` subtitle files) are placed in the `temp/` directory.
- AlfaazStudio automatically purges stale temporary files older than 24 hours upon server startup or via the manual `/api/v1/health/cleanup` endpoint.
- Users can manually purge the `temp/` directory at any point without impacting completed outputs or project configurations.

---

## 4. Network Activity

AlfaazStudio interacts with the network strictly under the following optional circumstances:
1. **Initial Model Download**: If local model weights are absent from the `models/` directory, the application requests the specific open-source weights from Hugging Face Hub (via official HTTPS endpoints). Once downloaded, the application can operate entirely offline with internet access disabled.
2. **Localhost Communication**: The frontend web interface communicates with the backend API exclusively over local loopback interfaces (`127.0.0.1` or `localhost`).

---

## 5. Security & Isolation

- **Docker Sandboxing**: AlfaazStudio provides container definitions (`infra/docker/`) allowing the entire studio to run in an isolated Docker container with bounded volume mounts and restricted network egress.
- **Input Sanitization**: All text and media inputs undergo sanitization to prevent command injection into underlying FFmpeg or audio processing binaries.

---

## 6. Inquiries & Community Verification

Because AlfaazStudio is completely open-source, the community is encouraged to audit our codebase, network activity, and build scripts to verify our zero-telemetry and offline guarantees.

