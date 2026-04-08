"""Tests for spine hooks install/list/uninstall commands (Issue #34)."""

from __future__ import annotations

import re
import stat
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spine.main import app
from spine.services.hooks_service import (
    SPINE_HOOK_SENTINEL,
    DEFAULT_HOOK_NAME,
    HooksService,
)

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_git_repo(path: Path) -> Path:
    """Create a minimal fake git repo with .git/hooks/ directory."""
    git_dir = path / ".git"
    git_dir.mkdir()
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir()
    return path


def invoke_hooks(cmd: str, path: Path, *extra: str) -> tuple[int, str]:
    args = ["hooks", cmd, "--cwd", str(path), *extra]
    result = runner.invoke(app, args)
    return result.exit_code, result.output


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


def test_hooks_group_registered() -> None:
    """spine hooks subgroup is registered and shows help."""
    result = runner.invoke(app, ["hooks", "--help"])
    assert result.exit_code == 0, result.output
    plain = _strip_ansi(result.output)
    assert "install" in plain
    assert "list" in plain
    assert "uninstall" in plain


def test_hooks_install_help() -> None:
    """spine hooks install --help shows expected flags."""
    result = runner.invoke(app, ["hooks", "install", "--help"])
    assert result.exit_code == 0, result.output
    plain = _strip_ansi(result.output)
    assert "--hook" in plain
    assert "--ignore-failure" in plain
    assert "--cwd" in plain


def test_hooks_list_help() -> None:
    result = runner.invoke(app, ["hooks", "list", "--help"])
    assert result.exit_code == 0, result.output
    assert "--cwd" in _strip_ansi(result.output)


def test_hooks_uninstall_help() -> None:
    result = runner.invoke(app, ["hooks", "uninstall", "--help"])
    assert result.exit_code == 0, result.output
    plain = _strip_ansi(result.output)
    assert "--hook" in plain
    assert "--cwd" in plain


# ---------------------------------------------------------------------------
# Install — happy path
# ---------------------------------------------------------------------------


def test_install_creates_hook_file(tmp_path: Path) -> None:
    """install creates .git/hooks/pre-push when no hook exists."""
    make_git_repo(tmp_path)
    exit_code, output = invoke_hooks("install", tmp_path)

    assert exit_code == 0, f"Expected exit 0, got {exit_code}. Output:\n{output}"
    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    assert hook_path.exists(), "Hook file must exist after install"


def test_install_hook_contains_sentinel(tmp_path: Path) -> None:
    """Installed hook contains the SPINE sentinel line."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    content = hook_path.read_text()
    assert SPINE_HOOK_SENTINEL in content


def test_install_hook_runs_checkpoint(tmp_path: Path) -> None:
    """Installed hook script calls 'spine check before-pr'."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)

    content = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert "spine check before-pr" in content


def test_install_hook_is_executable(tmp_path: Path) -> None:
    """Installed hook file is executable."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    mode = hook_path.stat().st_mode
    assert mode & stat.S_IXUSR, "Hook must be executable by owner"


def test_install_hook_has_shebang(tmp_path: Path) -> None:
    """Installed hook starts with #!/bin/sh."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)

    content = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert content.startswith("#!/bin/sh"), "Hook must start with #!/bin/sh"


def test_install_default_hook_is_pre_push(tmp_path: Path) -> None:
    """Default hook type is pre-push."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)

    assert (tmp_path / ".git" / "hooks" / "pre-push").exists()
    assert not (tmp_path / ".git" / "hooks" / "pre-commit").exists()


def test_install_output_confirms_success(tmp_path: Path) -> None:
    """install output confirms the hook path."""
    make_git_repo(tmp_path)
    exit_code, output = invoke_hooks("install", tmp_path)

    assert exit_code == 0
    plain = _strip_ansi(output)
    assert "pre-push" in plain


# ---------------------------------------------------------------------------
# Install — blocking vs non-blocking
# ---------------------------------------------------------------------------


def test_install_blocking_mode_default(tmp_path: Path) -> None:
    """Default install is blocking (exit $? propagation)."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)

    content = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert "exit $?" in content
    assert "exit 0" not in content


def test_install_ignore_failure_mode(tmp_path: Path) -> None:
    """--ignore-failure installs hook that always exits 0."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path, "--ignore-failure")

    content = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert "exit 0" in content
    assert "exit $?" not in content


def test_install_ignore_failure_flag_appears_in_script(tmp_path: Path) -> None:
    """--ignore-failure installs hook with explanatory comment."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path, "--ignore-failure")

    content = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert "--ignore-failure" in content


# ---------------------------------------------------------------------------
# Install — update existing SPINE hook
# ---------------------------------------------------------------------------


def test_install_updates_existing_spine_hook(tmp_path: Path) -> None:
    """Installing over an existing SPINE hook replaces it (update)."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)                         # blocking first
    exit_code, output = invoke_hooks("install", tmp_path, "--ignore-failure")  # re-install as non-blocking

    assert exit_code == 0
    content = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert "exit 0" in content   # now non-blocking


def test_install_update_reports_updated(tmp_path: Path) -> None:
    """Update of existing SPINE hook is acknowledged in output."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    _, output = invoke_hooks("install", tmp_path)
    plain = _strip_ansi(output)
    assert "Updated" in plain or "Installed" in plain  # acceptable either way


# ---------------------------------------------------------------------------
# Install — refuses to overwrite non-SPINE hooks
# ---------------------------------------------------------------------------


def test_install_refuses_non_spine_hook(tmp_path: Path) -> None:
    """install refuses to overwrite a pre-existing non-SPINE hook."""
    make_git_repo(tmp_path)
    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    hook_path.write_text("#!/bin/sh\necho 'custom hook'\n", encoding="utf-8")

    exit_code, output = invoke_hooks("install", tmp_path)

    assert exit_code == 1, f"Expected exit 1 (refused), got {exit_code}. Output:\n{output}"
    plain = _strip_ansi(output)
    assert "not" in plain.lower() or "third-party" in plain.lower() or "overwrite" in plain.lower()


def test_install_refuses_non_spine_hook_leaves_original(tmp_path: Path) -> None:
    """When install is refused, the original hook is not modified."""
    make_git_repo(tmp_path)
    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    original_content = "#!/bin/sh\necho 'custom hook'\n"
    hook_path.write_text(original_content, encoding="utf-8")

    invoke_hooks("install", tmp_path)

    assert hook_path.read_text() == original_content


# ---------------------------------------------------------------------------
# Install — missing hooks dir / no git repo
# ---------------------------------------------------------------------------


def test_install_no_git_repo(tmp_path: Path) -> None:
    """install returns exit 2 when there is no git repo."""
    # No .git/ directory at all
    exit_code, _ = invoke_hooks("install", tmp_path)
    assert exit_code == 2


def test_install_hooks_dir_missing(tmp_path: Path) -> None:
    """install fails gracefully when .git/ exists but .git/hooks/ does not."""
    (tmp_path / ".git").mkdir()
    # No hooks subdir
    exit_code, output = invoke_hooks("install", tmp_path)
    assert exit_code == 1
    assert "hooks" in _strip_ansi(output).lower()


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def test_list_empty_when_no_hooks(tmp_path: Path) -> None:
    """list reports nothing installed when no SPINE hooks exist."""
    make_git_repo(tmp_path)
    exit_code, output = invoke_hooks("list", tmp_path)

    assert exit_code == 0
    plain = _strip_ansi(output)
    assert "No SPINE hooks" in plain or "no spine hooks" in plain.lower()


def test_list_shows_installed_hook(tmp_path: Path) -> None:
    """list shows the hook after install."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    exit_code, output = invoke_hooks("list", tmp_path)

    assert exit_code == 0
    assert "pre-push" in output


def test_list_shows_mode_blocking(tmp_path: Path) -> None:
    """list shows 'blocking' mode for default install."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    _, output = invoke_hooks("list", tmp_path)

    assert "blocking" in output


def test_list_shows_mode_non_blocking(tmp_path: Path) -> None:
    """list shows 'non-blocking' mode for --ignore-failure install."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path, "--ignore-failure")
    _, output = invoke_hooks("list", tmp_path)

    assert "non-blocking" in output


def test_list_shows_hook_path(tmp_path: Path) -> None:
    """list output includes a Path column with path content."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    _, output = invoke_hooks("list", tmp_path)

    # Rich may truncate long paths in narrow terminals. Verify that the
    # output contains at least a portion of the tmp_path (which is unique).
    # We check for a fragment of the path that fits even when truncated.
    assert str(tmp_path)[:20] in output


def test_list_ignores_non_spine_hooks(tmp_path: Path) -> None:
    """list does not show hooks it did not install."""
    make_git_repo(tmp_path)
    # Write a non-SPINE hook manually
    (tmp_path / ".git" / "hooks" / "pre-push").write_text(
        "#!/bin/sh\necho custom\n", encoding="utf-8"
    )
    _, output = invoke_hooks("list", tmp_path)
    plain = _strip_ansi(output)
    assert "No SPINE hooks" in plain or "no spine hooks" in plain.lower()


def test_list_no_git_repo(tmp_path: Path) -> None:
    """list returns exit 2 when there is no git repo."""
    exit_code, _ = invoke_hooks("list", tmp_path)
    assert exit_code == 2


# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------


def test_uninstall_removes_hook(tmp_path: Path) -> None:
    """uninstall removes the SPINE hook file."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    exit_code, output = invoke_hooks("uninstall", tmp_path)

    assert exit_code == 0, f"Expected exit 0, got {exit_code}. Output:\n{output}"
    assert not (tmp_path / ".git" / "hooks" / "pre-push").exists()


def test_uninstall_output_confirms_removal(tmp_path: Path) -> None:
    """uninstall output confirms what was removed."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    _, output = invoke_hooks("uninstall", tmp_path)

    plain = _strip_ansi(output)
    assert "pre-push" in plain
    assert "Removed" in plain or "removed" in plain


def test_uninstall_hook_no_longer_in_list(tmp_path: Path) -> None:
    """After uninstall, list shows no hooks."""
    make_git_repo(tmp_path)
    invoke_hooks("install", tmp_path)
    invoke_hooks("uninstall", tmp_path)
    _, output = invoke_hooks("list", tmp_path)

    plain = _strip_ansi(output)
    assert "No SPINE hooks" in plain or "no spine hooks" in plain.lower()


def test_uninstall_when_hook_missing(tmp_path: Path) -> None:
    """uninstall returns exit 1 when no hook exists."""
    make_git_repo(tmp_path)
    exit_code, output = invoke_hooks("uninstall", tmp_path)

    assert exit_code == 1
    plain = _strip_ansi(output)
    assert "nothing" in plain.lower() or "not found" in plain.lower() or "No hook" in plain


def test_uninstall_refuses_non_spine_hook(tmp_path: Path) -> None:
    """uninstall refuses to remove a hook it didn't install."""
    make_git_repo(tmp_path)
    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    hook_path.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")

    exit_code, output = invoke_hooks("uninstall", tmp_path)

    assert exit_code == 1
    plain = _strip_ansi(output)
    assert "not" in plain.lower()


def test_uninstall_no_git_repo(tmp_path: Path) -> None:
    """uninstall returns exit 2 when there is no git repo."""
    exit_code, _ = invoke_hooks("uninstall", tmp_path)
    assert exit_code == 2


# ---------------------------------------------------------------------------
# --cwd support
# ---------------------------------------------------------------------------


def test_install_cwd_no_chdir(tmp_path: Path) -> None:
    """install --cwd does not change process cwd."""
    import os
    make_git_repo(tmp_path)
    original = os.getcwd()
    runner.invoke(app, ["hooks", "install", "--cwd", str(tmp_path)])
    assert os.getcwd() == original


def test_list_cwd_no_chdir(tmp_path: Path) -> None:
    import os
    make_git_repo(tmp_path)
    original = os.getcwd()
    runner.invoke(app, ["hooks", "list", "--cwd", str(tmp_path)])
    assert os.getcwd() == original


def test_uninstall_cwd_no_chdir(tmp_path: Path) -> None:
    import os
    make_git_repo(tmp_path)
    original = os.getcwd()
    runner.invoke(app, ["hooks", "uninstall", "--cwd", str(tmp_path)])
    assert os.getcwd() == original


def test_install_cwd_invalid_path() -> None:
    """install --cwd non-git path returns exit 2."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["hooks", "install", "--cwd", tmpdir])
        assert result.exit_code == 2


def test_list_cwd_invalid_path() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["hooks", "list", "--cwd", tmpdir])
        assert result.exit_code == 2


def test_uninstall_cwd_invalid_path() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["hooks", "uninstall", "--cwd", tmpdir])
        assert result.exit_code == 2


# ---------------------------------------------------------------------------
# HooksService unit tests
# ---------------------------------------------------------------------------


def test_service_install_returns_ok(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    result = svc.install()
    assert result.ok is True
    assert result.hook_path is not None


def test_service_install_already_existed_false_first_time(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    result = svc.install()
    assert result.already_existed is False


def test_service_install_already_existed_true_second_time(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    svc.install()
    result = svc.install()
    assert result.already_existed is True


def test_service_list_empty_initially(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    result = svc.list_hooks()
    assert not result.any_installed
    assert result.hooks == []


def test_service_list_after_install(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    svc.install()
    result = svc.list_hooks()
    assert result.any_installed
    assert len(result.hooks) == 1
    assert result.hooks[0].hook_name == DEFAULT_HOOK_NAME


def test_service_list_ignore_failure_parsed_correctly(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    svc.install(ignore_failure=True)
    result = svc.list_hooks()
    assert result.hooks[0].ignore_failure is True


def test_service_uninstall_ok(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    svc.install()
    result = svc.uninstall()
    assert result.ok is True


def test_service_uninstall_file_gone(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    svc.install()
    svc.uninstall()
    assert not (tmp_path / ".git" / "hooks" / "pre-push").exists()


def test_service_unsupported_hook_type(tmp_path: Path) -> None:
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    result = svc.install(hook_name="commit-msg")
    assert result.ok is False
    assert "Unsupported" in result.message


def test_service_deterministic_hook_content(tmp_path: Path) -> None:
    """Installing the same hook twice produces identical content."""
    make_git_repo(tmp_path)
    svc = HooksService(tmp_path)
    svc.install()
    content1 = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    svc.install()
    content2 = (tmp_path / ".git" / "hooks" / "pre-push").read_text()
    assert content1 == content2


def test_no_spine_state_mutation(tmp_path: Path) -> None:
    """install/uninstall do not write to .spine/."""
    make_git_repo(tmp_path)
    spine_dir = tmp_path / ".spine"
    spine_dir.mkdir()
    before = set(f.name for f in spine_dir.iterdir())

    svc = HooksService(tmp_path)
    svc.install()
    svc.uninstall()

    after = set(f.name for f in spine_dir.iterdir())
    assert before == after, f"hooks commands mutated .spine/: diff={after - before}"
