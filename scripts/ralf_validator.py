#!/usr/bin/env python3
"""
RALF Mode Self-Review Validator
Autonomously checks if phase is complete and ready to proceed
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class RalfValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.checks_passed = 0
        self.checks_total = 0
        self.errors = []

    def check_file_exists(self, path: str, description: str) -> bool:
        """Check if a file exists"""
        self.checks_total += 1
        file_path = self.project_root / path
        if file_path.exists():
            self.checks_passed += 1
            print(f"✅ {description}: {path}")
            return True
        else:
            self.errors.append(f"Missing file: {path}")
            print(f"❌ {description}: {path} NOT FOUND")
            return False

    def check_directory_exists(self, path: str, description: str) -> bool:
        """Check if a directory exists"""
        self.checks_total += 1
        dir_path = self.project_root / path
        if dir_path.exists() and dir_path.is_dir():
            self.checks_passed += 1
            print(f"✅ {description}: {path}")
            return True
        else:
            self.errors.append(f"Missing directory: {path}")
            print(f"❌ {description}: {path} NOT FOUND")
            return False

    def check_file_content(self, path: str, required_strings: List[str], description: str) -> bool:
        """Check if file contains required content"""
        self.checks_total += 1
        file_path = self.project_root / path
        if not file_path.exists():
            self.errors.append(f"File not found for content check: {path}")
            print(f"❌ {description}: {path} NOT FOUND")
            return False

        content = file_path.read_text(encoding="utf-8")
        missing = []
        for req in required_strings:
            if req not in content:
                missing.append(req)

        if not missing:
            self.checks_passed += 1
            print(f"✅ {description}: {path}")
            return True
        else:
            self.errors.append(f"Missing content in {path}: {missing}")
            print(f"❌ {description}: {path} MISSING: {missing}")
            return False

    def calculate_confidence(self) -> float:
        """Calculate confidence score"""
        if self.checks_total == 0:
            return 0.0
        return self.checks_passed / self.checks_total

    def validate_phase_1(self) -> Tuple[float, List[str]]:
        """Validate Phase 1 completion"""
        print("\n=== RALF Mode: Phase 1 Self-Review ===\n")

        # Check folder structure
        self.check_directory_exists("backend", "Backend directory")
        self.check_directory_exists("frontend", "Frontend directory")
        self.check_directory_exists("infra", "Infrastructure directory")
        self.check_directory_exists("models", "Models directory")
        self.check_directory_exists("outputs", "Outputs directory")
        self.check_directory_exists("temp", "Temp directory")

        # Check documentation files
        self.check_file_exists("MODEL_LICENSES.md", "Model licenses doc")
        self.check_file_exists("ARCHITECTURE.md", "Architecture doc")
        self.check_file_exists("PRIVACY.md", "Privacy policy")
        self.check_file_exists("PROJECT_PLAN.md", "Project plan")

        # Check backend initialization
        self.check_file_exists("backend/requirements.txt", "Backend requirements")
        self.check_file_exists("backend/pyproject.toml", "Backend pyproject")

        # Check frontend initialization
        self.check_file_exists("frontend/package.json", "Frontend package.json")
        self.check_file_exists("frontend/tsconfig.json", "Frontend TypeScript config")

        # Check environment file
        self.check_file_exists(".env.example", "Environment example file")

        # Check file content quality
        self.check_file_content(
            "MODEL_LICENSES.md",
            ["F5-TTS", "license", "personal use"],
            "Model licenses content",
        )

        self.check_file_content(
            "ARCHITECTURE.md",
            ["diagram", "component", "FastAPI", "Next.js"],
            "Architecture content",
        )

        confidence = self.calculate_confidence()

        print("\n=== Self-Review Summary ===")
        print(f"Checks Passed: {self.checks_passed}/{self.checks_total}")
        print(f"Confidence Score: {confidence:.2%}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\n=== Errors ===")
            for error in self.errors:
                print(f"  - {error}")

        return confidence, self.errors

    def validate_phase_2(self) -> Tuple[float, List[str]]:
        """Validate Phase 2 completion"""
        print("\n=== RALF Mode: Phase 2 Self-Review (Backend Foundation) ===\n")

        # Check backend folder structure
        self.check_directory_exists("backend/app/api/v1", "API v1 directory")
        self.check_directory_exists("backend/app/db", "Database layer directory")
        self.check_directory_exists("backend/app/schemas", "Schemas directory")
        self.check_directory_exists("backend/app/services", "Services directory")
        self.check_directory_exists("backend/app/core", "Core utilities directory")
        self.check_directory_exists("backend/alembic", "Alembic migrations directory")
        self.check_directory_exists("backend/tests", "Backend tests directory")

        # Check database models and session files
        self.check_file_exists("backend/app/db/base.py", "SQLAlchemy base")
        self.check_file_exists("backend/app/db/models.py", "Database models")
        self.check_file_exists("backend/app/db/session.py", "Async session management")

        # Check Alembic files
        self.check_file_exists("backend/alembic.ini", "Alembic configuration")
        self.check_file_exists("backend/alembic/env.py", "Alembic environment")

        # Check services
        self.check_file_exists("backend/app/services/storage.py", "Storage service")
        self.check_file_exists("backend/app/services/system.py", "System service")

        # Check core utilities
        self.check_file_exists("backend/app/core/logging.py", "Structured logging")
        self.check_file_exists("backend/app/core/security.py", "Security and traversal protection")
        self.check_file_exists("backend/app/core/exceptions.py", "Custom exceptions")

        # Check API routes
        self.check_file_exists("backend/app/api/v1/router.py", "API v1 router")
        self.check_file_exists("backend/app/api/v1/health.py", "Health endpoints")
        self.check_file_exists("backend/app/api/v1/system.py", "System endpoints")
        self.check_file_exists("backend/app/api/v1/voices.py", "Voices endpoints")
        self.check_file_exists("backend/app/api/v1/projects.py", "Projects endpoints")

        # Check test suite files
        self.check_file_exists("backend/tests/conftest.py", "Pytest fixtures")
        self.check_file_exists("backend/tests/test_health.py", "Health tests")
        self.check_file_exists("backend/tests/test_system.py", "System tests")
        self.check_file_exists("backend/tests/test_voices.py", "Voice tests")
        self.check_file_exists("backend/tests/test_projects.py", "Project tests")
        self.check_file_exists("backend/tests/test_storage.py", "Storage tests")
        self.check_file_exists("backend/tests/test_models.py", "Model tests")

        # Check content quality
        self.check_file_content(
            "backend/app/db/models.py",
            ["VoiceProfile", "Project", "AudioAsset", "VideoAsset", "Job"],
            "Database models content",
        )
        self.check_file_content(
            "backend/app/core/security.py",
            ["validate_safe_path", "validate_mime_type", "ALLOWED_AUDIO_MIMES"],
            "Security and MIME validation content",
        )
        self.check_file_content(
            "backend/app/api/v1/router.py",
            ["health_router", "system_router", "voices_router", "projects_router"],
            "Master router aggregation",
        )

        confidence = self.calculate_confidence()

        print("\n=== Self-Review Summary ===")
        print(f"Checks Passed: {self.checks_passed}/{self.checks_total}")
        print(f"Confidence Score: {confidence:.2%}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\n=== Errors ===")
            for error in self.errors:
                print(f"  - {error}")

        return confidence, self.errors

    def validate_phase_3(self) -> Tuple[float, List[str]]:
        """Validate Phase 3 completion"""
        print("\n=== RALF Mode: Phase 3 Self-Review (Mock TTS & Urdu Utils) ===\n")

        # Check directories
        self.check_directory_exists("backend/app/services/tts", "TTS services directory")
        self.check_directory_exists("backend/app/utils", "Utilities directory")

        # Check TTS provider files
        self.check_file_exists("backend/app/services/tts/provider.py", "TTS Provider Protocol")
        self.check_file_exists("backend/app/services/tts/mock_provider.py", "Mock TTS Provider")
        self.check_file_exists("backend/app/services/tts/factory.py", "TTS Provider Factory")

        # Check Urdu text utility files
        self.check_file_exists("backend/app/utils/urdu_text.py", "Urdu Text Utilities")

        # Check Celery and Queue files
        self.check_file_exists("backend/app/core/celery_app.py", "Celery configuration")
        self.check_file_exists("backend/app/services/queue.py", "Queue service & tasks")

        # Check API & Schemas
        self.check_file_exists("backend/app/schemas/job.py", "Job schemas")
        self.check_file_exists("backend/app/api/v1/jobs.py", "Job API endpoints")

        # Check tests
        self.check_file_exists("backend/tests/test_mock_tts.py", "Mock TTS tests")
        self.check_file_exists("backend/tests/test_urdu_text.py", "Urdu text tests")
        self.check_file_exists("backend/tests/test_job_queue.py", "Job queue tests")
        self.check_file_exists("backend/tests/test_pronunciation_dict.py", "Pronunciation dict tests")

        # Check content quality
        self.check_file_content(
            "backend/app/services/tts/provider.py",
            ["TTSProvider", "TTSResult", "WordTimestamp"],
            "TTS provider protocol definitions",
        )
        self.check_file_content(
            "backend/app/services/tts/mock_provider.py",
            ["MockTTSProvider", "440", "validate_speed"],
            "Mock provider sine generation and speed",
        )
        self.check_file_content(
            "backend/app/utils/urdu_text.py",
            ["UrduTextNormalizer", "PronunciationDictionary", "split_verses", "split_couplets"],
            "Urdu text normalizer and poetry chunking",
        )
        self.check_file_content(
            "backend/app/core/celery_app.py",
            ["Celery", "celery_app"],
            "Celery application instance",
        )
        self.check_file_content(
            "backend/app/services/queue.py",
            ["execute_audio_generation", "create_task_chain", "mark_job_cancelled"],
            "Queue audio processing and chaining",
        )
        self.check_file_content(
            "backend/app/api/v1/projects.py",
            ["generate-audio", "BackgroundTasks"],
            "Projects audio generation endpoint",
        )

        confidence = self.calculate_confidence()

        print("\n=== Self-Review Summary ===")
        print(f"Checks Passed: {self.checks_passed}/{self.checks_total}")
        print(f"Confidence Score: {confidence:.2%}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\n=== Errors ===")
            for error in self.errors:
                print(f"  - {error}")

        return confidence, self.errors

    def update_progress_file(self, phase: int, confidence: float, errors: List[str]):
        """Update PROGRESS.md file"""
        phase_names = {
            1: "Architecture & Compliance",
            2: "Backend Foundation",
            3: "Mock TTS & Urdu Utils",
            4: "Real Urdu TTS Integration",
            5: "Frontend Foundation",
            6: "Audio Editor",
            7: "Reel Rendering",
            8: "Production Hardening",
        }
        phase_name = phase_names.get(phase, f"Phase {phase}")

        progress_file = self.project_root / "PROGRESS.md"
        if not progress_file.exists():
            print("Warning: PROGRESS.md not found, creating...")
            progress_file.write_text("# AlfaazStudio Progress\n", encoding="utf-8")

        content = progress_file.read_text(encoding="utf-8")

        # Update current phase
        content = re.sub(r"\*\*Current Phase\*\*:\s*.*", f"**Current Phase**: {phase} ({phase_name})", content)

        # Update progress percentage
        progress_pct = (phase / 8.0) * 100
        content = re.sub(r"\*\*Overall Progress\*\*:\s*.*", f"**Overall Progress**: {progress_pct:.1f}% ({phase}/8 phases)", content)

        # Update confidence
        content = re.sub(r"\*\*Confidence Score\*\*:\s*.*", f"**Confidence Score**: {confidence:.2%}", content)

        # Update status
        status = "✅ Complete" if confidence >= 0.85 else "❌ Needs Review"
        section_pattern = rf"(## Phase {phase}: [^\n]+[\s\S]*?### Status:\s*)[^\n]+"
        content = re.sub(section_pattern, rf"\g<1>{status}", content)

        progress_file.write_text(content, encoding="utf-8")
        print("\n✅ PROGRESS.md updated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RALF Mode Phase Validator")
    parser.add_argument("--phase", type=int, default=3, help="Phase number to validate (1-8)")
    args = parser.parse_args()

    validator = RalfValidator()
    if args.phase == 1:
        confidence, errors = validator.validate_phase_1()
    elif args.phase == 2:
        confidence, errors = validator.validate_phase_2()
    elif args.phase == 3:
        confidence, errors = validator.validate_phase_3()
    else:
        print(f"Phase {args.phase} validator not yet implemented")
        sys.exit(1)

    validator.update_progress_file(args.phase, confidence, errors)

    if confidence >= 0.85:
        print(f"\n🎉 Phase {args.phase} PASSED self-review. Proceeding...")
        sys.exit(0)
    else:
        print(f"\n⚠️ Phase {args.phase} FAILED self-review (confidence: {confidence:.2%}). Auto-fixing...")
        sys.exit(1)