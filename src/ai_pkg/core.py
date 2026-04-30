"""Package installation logic (called by the progress screen)."""
from __future__ import annotations

# NOTE: In v2, actual installation is handled by the async ProgressScreen
# which streams subprocess output directly to the TUI.
# This module is kept for potential future CLI-only use or testing.

import logging
import shutil
import subprocess

logger = logging.getLogger(__name__)


def install_packages(
    pkgs: list[str],
    dry_run: bool = False,
    auto_yes: bool = False,
    aur_helper: str = "yay",
) -> bool:
    """Synchronously install packages (used outside the TUI context).

    Returns True on success, False on failure.
    """
    if not pkgs:
        logger.warning("No packages to install")
        return True

    pacman_pkgs = [p for p in pkgs if not p.startswith("aur:")]
    aur_pkgs = [p[4:] for p in pkgs if p.startswith("aur:")]

    if pacman_pkgs:
        cmd = ["sudo", "pacman", "-S", "--needed"]
        if auto_yes:
            cmd.append("--noconfirm")
        cmd.extend(pacman_pkgs)
        if dry_run:
            print(f"[DRY RUN] {' '.join(cmd)}")
        else:
            result = subprocess.run(cmd)
            if result.returncode != 0:
                logger.error("pacman failed with exit %d", result.returncode)
                return False

    if aur_pkgs:
        if not shutil.which(aur_helper):
            logger.warning("'%s' not found — skipping AUR packages", aur_helper)
        else:
            cmd = [aur_helper, "-S", "--needed"]
            if auto_yes:
                cmd.append("--noconfirm")
            cmd.extend(aur_pkgs)
            if dry_run:
                print(f"[DRY RUN] {' '.join(cmd)}")
            else:
                result = subprocess.run(cmd)
                if result.returncode != 0:
                    logger.error("%s failed with exit %d", aur_helper, result.returncode)
                    return False

    return True