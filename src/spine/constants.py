"""Single source of truth for all SPINE path names and version constants."""

from __future__ import annotations

SPINE_DIR = ".spine"
SPINE_VERSION = "0.1"

# --- YAML state files ---
MISSION_FILE = "mission.yaml"
CONSTRAINTS_FILE = "constraints.yaml"

# --- JSONL append logs ---
OPPORTUNITIES_FILE = "opportunities.jsonl"
NOT_NOW_FILE = "not_now.jsonl"
EVIDENCE_FILE = "evidence.jsonl"
DECISIONS_FILE = "decisions.jsonl"
DRIFT_FILE = "drift.jsonl"
RUNS_FILE = "runs.jsonl"

# --- SQLite placeholder (Phase 1: empty file, never written as SQLite) ---
STATE_DB_FILE = "state.db"

# --- Subdirectories ---
REVIEWS_DIR = "reviews"
BRIEFS_DIR = "briefs"
SKILLS_DIR = "skills"
CHECKS_DIR = "checks"
DRAFTS_DIR = "drafts"

# --- Artifact manifest ---
ARTIFACT_MANIFEST_FILE = "artifact_manifest.json"

# --- Repo-root files ---
AGENTS_MD = "AGENTS.md"
CLAUDE_MD = "CLAUDE.md"
CLAUDE_SETTINGS_PATH = ".claude/settings.json"
CODEX_CONFIG_PATH = ".codex/config.toml"
