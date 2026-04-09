"""Tests for spine mcp serve — startup smoke tests + end-to-end tool-call coverage."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from spine.main import app
from typer.testing import CliRunner

runner = CliRunner()

# MCP protocol version used for handshake in subprocess tests.
_MCP_PROTOCOL_VERSION = "2025-03-26"


def make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo (just a .git dir)."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def run_init(tmp_path: Path, *extra_args: str) -> tuple[int, str, str]:
    result = runner.invoke(app, ["init", "--cwd", str(tmp_path), *extra_args])
    return result.exit_code, result.output, ""



# ---------------------------------------------------------------------------
# Startup smoke tests
# ---------------------------------------------------------------------------


def test_mcp_serve_starts_without_error(tmp_path: Path) -> None:
    """
    spine mcp serve starts without crashing on import.

    Sends an empty stdin (EOF) so the server exits promptly.
    The key assertion: stderr must NOT contain MCP-import or module errors.
    """
    make_git_repo(tmp_path)
    run_init(tmp_path)

    result = subprocess.run(
        [sys.executable, "-m", "spine", "mcp", "serve"],
        cwd=str(tmp_path),
        input=b"",
        capture_output=True,
        timeout=10,
    )

    stderr = result.stderr.decode(errors="replace").lower()
    # Any of these in stderr means the MCP layer itself is broken.
    for bad_phrase in ("no module named", "importerror", "nameerror", "mcp package not installed"):
        assert bad_phrase not in stderr, (
            f"MCP startup failure detected — '{bad_phrase}' in stderr:\n{result.stderr.decode()}"
        )


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


# ---------------------------------------------------------------------------
# End-to-end tool-call tests (protocol level)
# ---------------------------------------------------------------------------


def _mcp_session(tmp_path: Path):
    """
    Context manager: start spine mcp serve as a subprocess, return a helper
    that can send JSON-RPC messages and read line-by-line responses.

    Keeps stdin open so the server doesn't exit prematurely due to EOF;
    closes stdin when the context exits so the server shuts down cleanly.
    """
    import contextlib

    @contextlib.contextmanager
    def _session():
        proc = subprocess.Popen(
            [sys.executable, "-m", "spine", "mcp", "serve"],
            cwd=str(tmp_path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            def send(msg: dict) -> None:
                proc.stdin.write((json.dumps(msg) + "\n").encode())
                proc.stdin.flush()

            def recv() -> dict:
                line = proc.stdout.readline()
                if not line:
                    raise RuntimeError(
                        f"Server closed stdout unexpectedly.\n"
                        f"stderr: {proc.stderr.read().decode(errors='replace')}"
                    )
                return json.loads(line.decode(errors="replace").strip())

            def handshake() -> dict:
                """Perform MCP initialize handshake; return initialize response."""
                send({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": _MCP_PROTOCOL_VERSION,
                        "capabilities": {},
                        "clientInfo": {"name": "pytest", "version": "0.0.1"},
                    },
                })
                init_response = recv()
                send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
                return init_response

            yield send, recv, handshake
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    return _session()


def test_mcp_tool_call_mission_get_returns_text_content(tmp_path: Path) -> None:
    """
    End-to-end: MCP tool call for mission_get returns valid TextContent.

    Proves:
    - MCP server accepts the initialize handshake
    - tools/call for mission_get executes without error
    - Response contains content with type='text'
    - No NameError, TypeError, or other runtime crash in tool dispatch
    """
    make_git_repo(tmp_path)
    run_init(tmp_path)

    with _mcp_session(tmp_path) as (send, recv, handshake):
        init_resp = handshake()
        assert "result" in init_resp, f"Unexpected initialize response: {init_resp}"

        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "mission_get", "arguments": {}},
        })
        tool_response = recv()

    assert "error" not in tool_response, (
        f"Tool call returned an error: {tool_response.get('error')}"
    )
    assert "result" in tool_response, f"No 'result' in tool response: {tool_response}"

    content = tool_response["result"].get("content", [])
    assert len(content) > 0, "Tool response has empty content list"

    first = content[0]
    assert first.get("type") == "text", f"Expected type='text', got: {first}"
    text = first.get("text", "")
    assert text, "TextContent.text is empty"

    # The text should be JSON with mission fields.
    mission_data = json.loads(text)
    assert "title" in mission_data or "status" in mission_data, (
        f"mission_get response missing expected fields: {mission_data}"
    )


def test_mcp_tools_list_returns_expected_tools(tmp_path: Path) -> None:
    """
    End-to-end: tools/list returns the expected set of SPINE tools.

    Proves the server's list_tools handler executes without crashing.
    """
    make_git_repo(tmp_path)
    run_init(tmp_path)

    with _mcp_session(tmp_path) as (send, recv, handshake):
        handshake()

        send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {},
        })
        tools_response = recv()

    assert "error" not in tools_response, f"tools/list error: {tools_response.get('error')}"
    assert "result" in tools_response, f"No result in tools/list response: {tools_response}"

    tools = tools_response["result"]["tools"]
    tool_names = {t["name"] for t in tools}
    expected = {"mission_get", "evidence_add", "decision_add", "drift_scan"}
    assert expected.issubset(tool_names), (
        f"Missing expected tools. Got: {tool_names}"
    )
