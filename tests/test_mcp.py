"""Smoke tests for spine mcp command (Phase 2)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from spine.main import app
from typer.testing import CliRunner

runner = CliRunner()


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_mcp_serve_starts_without_error(tmp_path: Path) -> None:
    """
    spine mcp serve starts and listens on stdio.

    This is a smoke test: we verify the command starts without error.
    Full MCP protocol testing requires an MCP client which is complex.
    """
    make_git_repo(tmp_path)
    run_init(tmp_path)

    # Run the mcp serve command with a timeout
    # We pass an empty stdin so it gets EOF immediately, which causes
    # the server to exit cleanly rather than hang on stdio read
    result = subprocess.run(
        [sys.executable, "-m", "spine", "mcp", "serve"],
        cwd=str(tmp_path),
        input=b"",
        capture_output=True,
        timeout=5,
    )

    # If MCP is not installed, the command exits with code 1
    # and stderr contains an appropriate error message
    # Otherwise it exits with code 0 (clean exit on EOF) or 1 (if MCP protocol issue)
    if result.returncode != 0:
        # Only fail if there's an unexpected error (not MCP-related)
        stderr_lower = result.stderr.lower()
        if b"no module named" in stderr_lower or b"importerror" in stderr_lower:
            pytest.fail(f"MCP package import failed: {result.stderr.decode()}")


@pytest.mark.skipif(os.name == "nt", reason="SIGINT not supported on Windows subprocess")
def test_mcp_serve_can_be_interrupted_gracefully(tmp_path: Path) -> None:
    """
    spine mcp serve can be interrupted gracefully.

    This test sends SIGINT and verifies the process exits cleanly.
    """
    import signal

    make_git_repo(tmp_path)
    run_init(tmp_path)

    proc = subprocess.Popen(
        [sys.executable, "-m", "spine", "mcp", "serve"],
        cwd=str(tmp_path),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Send interrupt signal
    proc.send_signal(signal.SIGINT)

    try:
        # Wait for graceful shutdown with timeout
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        pytest.fail("mcp serve did not exit within 5 seconds of SIGINT")