# AlfaazStudio - Model Licenses & Legal Compliance

## 1. Executive Summary & Compliance Stance

AlfaazStudio is an open-source, local-first studio designed for generating high-fidelity Urdu poetry voice-overs and Instagram Reels. Because speech synthesis models utilize diverse datasets and architectures, licensing compliance is strictly observed.

**AlfaazStudio is categorized as PERSONAL USE ONLY** when deployed with non-commercial voice weights (such as F5-TTS or Coqui XTTS-v2). Users wishing to use generated outputs for commercial purposes must select an Apache 2.0 / MIT licensed model or train custom weights on proprietary, commercially cleared Urdu voice datasets.

---

## 2. Model License Inventory

| Model / Component | Primary Architecture | License | Permitted Use | Commercial Rights | Notes |
|---|---|---|---|---|---|
| **F5-TTS (Urdu Fine-Tune)** | Flow Matching DiT | CC-BY-NC 4.0 / Research | **Personal use & non-commercial research** | ❌ No | High expressive nuance for Urdu poetry and emotional cadence. Strictly personal use. |
| **MeloTTS** | VITS / Flow-based | MIT License | Personal & Commercial | ✅ Yes | Lightweight, fast CPU inference, multilingual including South Asian variants. |
| **Piper TTS (Urdu)** | VITS / ONNX | MIT / GPL 3.0 | Personal & Commercial (variant dependent) | ✅ Yes | Ultra-fast offline inference, minimal RAM/VRAM footprint. |
| **Coqui XTTS-v2** | Autoregressive + Diffusion | Coqui Public Model License (CPML) | **Personal use & non-commercial** | ❌ No | Requires commercial agreement with Coqui successor for commercial use. |
| **OpenAI Whisper (Urdu ASR)** | Transformer Encoder-Decoder | MIT License | Personal & Commercial | ✅ Yes | Used locally for timestamp alignment and word-level subtitle synchronization. |
| **Edge-TTS (Local Bridge)** | Cloud Synthesizer Protocol | Microsoft Terms of Service | Personal evaluation | ❌ No | Fallback driver for quick mockups without GPU. |
| **Mock TTS Engine** | Deterministic Synth (NumPy/SciPy) | Apache 2.0 | Unrestricted | ✅ Yes | Offline test harness for automated CI/CD and unit testing without downloading model weights. |

---

## 3. Deep-Dive on Core Synthesizers

### 3.1 F5-TTS
- **License Type**: Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0) or upstream research license.
- **Grant**: Permits copying, distribution, remixing, and adapting the material for non-commercial purposes.
- **Constraints**:
  - The model weights and any direct voice clones created with F5-TTS must not be used for commercial advantage or monetary compensation.
  - Attribution must be given to the upstream authors (SWivid / F5-TTS team).
- **AlfaazStudio Implementation**: When `DEFAULT_TTS_ENGINE=f5-tts`, AlfaazStudio operates in **personal use mode**. Output reels carry a personal/educational attribution watermark metadata tag unless explicitly disabled by the user for private playback.

### 3.2 MeloTTS
- **License Type**: MIT License.
- **Grant**: Unrestricted commercial and personal use with standard copyright and permission notices included.
- **Recommendation**: Default engine recommended for commercial creators seeking zero licensing exposure.

### 3.3 Piper TTS
- **License Type**: MIT / GPL (Model weights depend on specific dataset: typically public domain or CC-BY-SA).
- **Target**: Ultra-fast low-resource devices (embedded, low-spec laptops without dedicated NVIDIA GPU).

---

## 4. Voice Cloning & Ethical Audio Policy

Voice cloning technology introduces legal and ethical responsibilities. AlfaazStudio implements strict safeguards:

1. **Explicit Consent**: You must possess explicit legal authorization, power of attorney, or public domain status for any reference audio imported into AlfaazStudio for voice matching.
2. **No Impersonation**: Generating voice clones of living public figures, political personalities, or private individuals without their notarized consent is strictly prohibited by our Acceptable Use Policy.
3. **Deepfake Prevention**: Rendered media files contain embedded metadata tags:
   - `X-Synthesized-By: AlfaazStudio`
   - `X-Synthesis-Engine: <EngineName>`
   - `X-License-Mode: personal-use-only`

---

## 5. Compliance Checklist for Users

Before distributing or publishing generated audio/video reels:
- [ ] Verify that your selected TTS engine corresponds to your distribution goal (Commercial vs. Personal).
- [ ] If using **F5-TTS**, confirm your channel/page is strictly non-monetized and marked for personal use.
- [ ] Confirm reference audio samples are copyright-cleared or self-recorded.
- [ ] Ensure font licenses for Urdu typography (e.g., Jameel Noori Nastaleeq / Noto Nastaliq Urdu) are respected. Noto fonts are licensed under the SIL Open Font License (OFL 1.1).

---

## 6. Model Weight Acquisition & Storage

No model weights are distributed inside the Git repository. Weights are retrieved on demand:
- Hugging Face Hub (cached in `models/` directory, excluded via `.gitignore`).
- Local hashes (SHA-256) are verified on load to prevent tampering.
- Offline mode: If no internet connection is detected, AlfaazStudio automatically falls back to cached weights or the built-in Mock TTS engine.

