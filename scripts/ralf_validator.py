#!/usr/bin/env python3
"""
RALF Mode Self-Review Validator
Autonomously checks if phase is complete and ready to proceed
"""

import os
import sys
import json
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
            "Model licenses content"
        )
        
        self.check_file_content(
            "ARCHITECTURE.md",
            ["diagram", "component", "FastAPI", "Next.js"],
            "Architecture content"
        )
        
        confidence = self.calculate_confidence()
        
        print(f"\n=== Self-Review Summary ===")
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
        import re
        progress_file = self.project_root / "PROGRESS.md"
        if not progress_file.exists():
            print("Warning: PROGRESS.md not found, creating...")
            progress_file.write_text("# AlfaazStudio Progress\n", encoding="utf-8")
        
        content = progress_file.read_text(encoding="utf-8")
        
        # Update current phase
        content = re.sub(r"\*\*Current Phase\*\*:\s*.*", f"**Current Phase**: {phase}", content)
        
        # Update confidence
        content = re.sub(r"\*\*Confidence Score\*\*:\s*.*", f"**Confidence Score**: {confidence:.2%}", content)
        
        # Update status for Phase 1
        status = "✅ Complete" if confidence >= 0.85 else "❌ Needs Review"
        content = re.sub(r"(## Phase 1: Architecture & Compliance[\s\S]*?### Status:\s*)[^\n]+", rf"\g<1>{status}", content)
        
        progress_file.write_text(content, encoding="utf-8")
        print(f"\n✅ PROGRESS.md updated")

if __name__ == "__main__":
    validator = RalfValidator()
    confidence, errors = validator.validate_phase_1()
    validator.update_progress_file(1, confidence, errors)
    
    if confidence >= 0.85:
        print("\n🎉 Phase 1 PASSED self-review. Proceeding to Phase 2...")
        exit(0)
    else:
        print(f"\n⚠️ Phase 1 FAILED self-review (confidence: {confidence:.2%}). Auto-fixing...")
        exit(1)