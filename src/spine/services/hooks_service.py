"""SPINE hooks service — local, explicit, opt-in git hook management."""

from __future__ import annotations

import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPINE_HOOK_SENTINEL = "# SPINE: managed hook — spine hooks install"

# The one hook type SPINE manages: pre-push runs before `git push`,
# which is the step immediately before opening a PR.  It is the cleanest
# native git hook for preflight governance enforcement.
DEFAULT_HOOK_NAME: Literal["pre-push"] = "pre-push"

SUPPORTED_HOOKS: tuple[str, ...] = ("pre-push",)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class InstalledHook:
    """Metadata for a single SPINE-managed hook."""

    hook_name: str          # e.g. "pre-push"
    hook_path: Path         # absolute path to the hook file
    ignore_failure: bool    # whether the hook is installed in non-blocking mode


@dataclass
class InstallResult:
    ok: bool
    message: str
    hook_path: Path | None = None
    already_existed: bool = False    # True when an existing SPINE hook was replaced


@dataclass
class UninstallResult:
    ok: bool
    message: str
    hook_path: Path | None = None


@dataclass
class ListResult:
    hooks: list[InstalledHook] = field(default_factory=list)

    @property
    def any_installed(self) -> bool:
        return bool(self.hooks)


# ---------------------------------------------------------------------------
# Hook script builder
# ---------------------------------------------------------------------------


def _build_hook_script(ignore_failure: bool) -> str:
    """Return the shell script content for the SPINE pre-push hook."""
    lines = [
        "#!/bin/sh",
        SPINE_HOOK_SENTINEL,
        "# To view: uv run spine hooks list",
        "# To remove: uv run spine hooks uninstall",
        "",
        "uv run spine check before-pr",
    ]
    if ignore_failure:
        lines += [
            "# --ignore-failure: hook exits 0 regardless of checkpoint result",
            "exit 0",
        ]
    else:
        lines += [
            "exit $?",
        ]
    return "\n".join(lines) + "\n"


def _is_spine_hook(path: Path) -> bool:
    """Return True if the file at *path* contains the SPINE sentinel line."""
    try:
        content = path.read_text(encoding="utf-8")
        return SPINE_HOOK_SENTINEL in content
    except (OSError, UnicodeDecodeError):
        return False


def _parse_ignore_failure(path: Path) -> bool:
    """Return True if the installed hook was installed with --ignore-failure."""
    try:
        content = path.read_text(encoding="utf-8")
        return "--ignore-failure" in content
    except (OSError, UnicodeDecodeError):
        return False


# ---------------------------------------------------------------------------
# HooksService
# ---------------------------------------------------------------------------


class HooksService:
    """
    Local, explicit, opt-in SPINE hook management.

    All operations target the ``<repo_root>/.git/hooks/`` directory.
    No state is written outside ``.git/hooks/``.
    No background processes. No auto-install.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.hooks_dir = repo_root / ".git" / "hooks"

    # ------------------------------------------------------------------
    # Install
    # ------------------------------------------------------------------

    def install(
        self,
        hook_name: str = DEFAULT_HOOK_NAME,
        *,
        ignore_failure: bool = False,
    ) -> InstallResult:
        """
        Install a SPINE-managed hook into ``.git/hooks/<hook_name>``.

        Behaviour:
        - If the hooks dir does not exist, fail clearly.
        - If the hook file does not exist, create it.
        - If the hook file exists and is a SPINE hook, replace it (update).
        - If the hook file exists and is NOT a SPINE hook, refuse and tell the
          operator to remove or rename it first — SPINE will not overwrite
          third-party hooks silently.
        """
        if hook_name not in SUPPORTED_HOOKS:
            return InstallResult(
                ok=False,
                message=(
                    f"Unsupported hook type: {hook_name!r}. "
                    f"SPINE currently supports: {', '.join(SUPPORTED_HOOKS)}"
                ),
            )

        if not self.hooks_dir.exists():
            return InstallResult(
                ok=False,
                message=(
                    f"Hooks directory not found: {self.hooks_dir}\n"
                    "  Is this a valid git repository? Try running 'git init' first."
                ),
            )

        hook_path = self.hooks_dir / hook_name
        already_existed = False

        if hook_path.exists():
            if not _is_spine_hook(hook_path):
                return InstallResult(
                    ok=False,
                    message=(
                        f"A non-SPINE hook already exists at: {hook_path}\n"
                        "  SPINE will not overwrite third-party hooks.\n"
                        "  To proceed: rename or remove the existing hook, then re-run "
                        "'spine hooks install'."
                    ),
                    hook_path=hook_path,
                )
            already_existed = True

        script = _build_hook_script(ignore_failure=ignore_failure)
        hook_path.write_text(script, encoding="utf-8")

        # Make the hook executable (owner rwx, group+other rx).
        current = hook_path.stat().st_mode
        hook_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        mode_note = "non-blocking (--ignore-failure)" if ignore_failure else "blocking"
        action = "Updated" if already_existed else "Installed"
        return InstallResult(
            ok=True,
            message=(
                f"{action} SPINE {hook_name} hook at: {hook_path}\n"
                f"  Mode: {mode_note}\n"
                f"  The hook runs 'uv run spine check before-pr' before each push.\n"
                f"  To remove: spine hooks uninstall"
            ),
            hook_path=hook_path,
            already_existed=already_existed,
        )

    # ------------------------------------------------------------------
    # Uninstall
    # ------------------------------------------------------------------

    def uninstall(self, hook_name: str = DEFAULT_HOOK_NAME) -> UninstallResult:
        """
        Remove a SPINE-managed hook from ``.git/hooks/<hook_name>``.

        Only removes files that contain the SPINE sentinel line.
        Refuses to remove hooks it did not create.
        """
        if hook_name not in SUPPORTED_HOOKS:
            return UninstallResult(
                ok=False,
                message=(
                    f"Unsupported hook type: {hook_name!r}. "
                    f"SPINE currently supports: {', '.join(SUPPORTED_HOOKS)}"
                ),
            )

        hook_path = self.hooks_dir / hook_name

        if not hook_path.exists():
            return UninstallResult(
                ok=False,
                message=(
                    f"No hook found at: {hook_path}\n"
                    "  Nothing to uninstall."
                ),
                hook_path=hook_path,
            )

        if not _is_spine_hook(hook_path):
            return UninstallResult(
                ok=False,
                message=(
                    f"The hook at {hook_path} was not installed by SPINE.\n"
                    "  SPINE will not remove third-party hooks.\n"
                    "  Remove it manually if you no longer need it."
                ),
                hook_path=hook_path,
            )

        hook_path.unlink()
        return UninstallResult(
            ok=True,
            message=f"Removed SPINE {hook_name} hook from: {hook_path}",
            hook_path=hook_path,
        )

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_hooks(self) -> ListResult:
        """
        List SPINE-managed hooks installed in ``.git/hooks/``.

        Scans only for supported hook names; ignores all other files.
        """
        result = ListResult()

        if not self.hooks_dir.exists():
            return result

        for hook_name in SUPPORTED_HOOKS:
            hook_path = self.hooks_dir / hook_name
            if hook_path.exists() and _is_spine_hook(hook_path):
                result.hooks.append(
                    InstalledHook(
                        hook_name=hook_name,
                        hook_path=hook_path,
                        ignore_failure=_parse_ignore_failure(hook_path),
                    )
                )

        return result
