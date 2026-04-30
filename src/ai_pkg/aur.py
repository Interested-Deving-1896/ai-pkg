"""AUR and pacman package metadata enrichment.

Queries:
- Official packages: `pacman -Si <name>` (sync, subprocess)
- AUR packages:  AUR RPC v5 API (async, httpx)
"""
from __future__ import annotations

import asyncio
import logging
import subprocess
from typing import List

import httpx

from .backends.base import PackageSuggestion

logger = logging.getLogger(__name__)

_AUR_RPC = "https://aur.archlinux.org/rpc/v5/info"


# ── Official (pacman) ─────────────────────────────────────────────────────────

def _pacman_info(name: str) -> tuple[str, bool]:
    """Return (description, found) via pacman -Si."""
    try:
        out = subprocess.run(
            ["pacman", "-Si", name],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode != 0:
            return "", False
        for line in out.stdout.splitlines():
            if line.lower().startswith("description"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    return parts[1].strip(), True
        return "", True
    except Exception:
        return "", False


# ── AUR RPC ───────────────────────────────────────────────────────────────────

async def _aur_info_batch(names: List[str]) -> dict[str, str]:
    """Return {name: description} for AUR packages via RPC v5."""
    if not names:
        return {}
    params = [("arg[]", n) for n in names]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(_AUR_RPC, params=params)
            resp.raise_for_status()
            data = resp.json()
        return {r["Name"]: r.get("Description", "") for r in data.get("results", [])}
    except Exception as e:
        logger.warning("AUR RPC error: %s", e)
        return {}


# ── Public API ────────────────────────────────────────────────────────────────

async def enrich(packages: List[PackageSuggestion]) -> List[PackageSuggestion]:
    """Fill in real descriptions and mark unavailable packages.

    Mutates the list in place and returns it.
    """
    official = [p for p in packages if p.source == "official"]
    aur = [p for p in packages if p.source == "aur"]

    # Fetch AUR descriptions async
    aur_descriptions = await _aur_info_batch([p.name for p in aur])

    # Check official packages in a thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()

    async def check_official(pkg: PackageSuggestion) -> None:
        desc, found = await loop.run_in_executor(None, _pacman_info, pkg.name)
        pkg.available = found
        if desc and not pkg.description:
            pkg.description = desc

    await asyncio.gather(*[check_official(p) for p in official])

    # Fallback: check missing official packages in AUR
    missing_official = [p for p in official if not p.available]
    if missing_official:
        missing_names = [p.name for p in missing_official]
        fallback_aur = await _aur_info_batch(missing_names)
        for p in missing_official:
            if p.name in fallback_aur:
                p.source = "aur"
                p.available = True
                if not p.description:
                    p.description = fallback_aur[p.name]

    # Apply AUR results
    for pkg in aur:
        aur_desc = aur_descriptions.get(pkg.name)
        if aur_desc is not None:
            pkg.available = True
            if not pkg.description:
                pkg.description = aur_desc
        else:
            pkg.available = False  # not found in AUR

    return packages
