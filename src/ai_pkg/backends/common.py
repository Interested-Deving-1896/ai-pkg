"""Shared helpers: prompt template and JSON extraction."""
from __future__ import annotations

import json
import logging
from typing import Any, List

from .base import PackageSuggestion, SuggestionResult

logger = logging.getLogger(__name__)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are ai-pkg, a precise Arch Linux package and environment assistant running \
interactively in a TUI. Your job is to produce a minimal, correct action plan \
for the user's current goal.

OUTPUT FORMAT — respond with ONLY a single JSON object. No markdown, no prose, \
no code fences. Schema:

{
  "packages": [
    {
      "name": "<exact Arch / AUR package name>",
      "source": "official" | "aur",
      "description": "<one short sentence: what the package is>",
      "reason": "<one short sentence: why it is needed for this specific goal>",
      "alternates": ["<alt-name>", "aur:<aur-alt>"]
    }
  ],
  "env_steps": [
    "<shell command>",
    "<shell command>"
  ]
}

PACKAGE RULES:
1. Use real, installable package names from the Arch repos or AUR right now.
   - For official: `source = "official"` (installed via pacman)
   - For AUR:      `source = "aur"`      (installed via yay / paru)
   - NEVER prefix `name` with "aur:"; set `source = "aur"` instead.
2. Be minimal — only include packages directly required by the goal.
3. Do not hallucinate packages. If unsure of the exact name, use `alternates`.
4. Do not suggest GUI apps unless the user explicitly asks for them.
5. Always respond for the current Arch Linux ecosystem (rolling release, 2024+).

ENV_STEPS RULES — these are run verbatim in a shell. They MUST be correct:
A. Each command must be a real, complete, working shell command.
   BAD:  "spicetify"          (does nothing without a subcommand)
   GOOD: "spicetify backup apply enable-devtools"
B. NEVER use placeholder values. Users cannot edit them unless they know to.
   BAD:  "git config --global user.name 'Your Name'"
   GOOD: omit git config entirely — it's personal, not part of the tool setup.
C. Do NOT repeat package installation. Packages are already installed via pacman/yay.
   BAD:  "pip install spicetify-cli"  (if it's already a package above)
D. Only include steps that are REQUIRED for the tool to function after install.
   Skip optional/cosmetic configuration unless the user explicitly asked for it.
E. If a tool requires no post-install steps, return `"env_steps": []`.
F. For spicetify: the correct post-install commands are:
   "spicetify backup apply enable-devtools"
   and optionally "spicetify apply" to apply the current theme.
"""


def extract_json(text: str) -> Any:
    """Extract the first JSON object from arbitrary text, even if wrapped in prose."""
    text = text.strip()
    # fast path — pure JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # strip common wrappers like ```json ... ``` or ``` ... ```
    import re
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # last resort: grab the outermost { ... }
    for open_c, close_c in [('{', '}'), ('[', ']')]:
        start = text.find(open_c)
        end   = text.rfind(close_c) + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return None


def parse_result(data: Any, goal: str) -> SuggestionResult:
    """Convert raw parsed JSON into a SuggestionResult."""
    if not isinstance(data, dict):
        return SuggestionResult([], [], goal, error="Unexpected response shape from AI")

    pkgs: List[PackageSuggestion] = []
    for p in data.get("packages", []):
        if isinstance(p, str):
            name   = p[4:] if p.startswith("aur:") else p
            source = "aur" if p.startswith("aur:") else "official"
            pkgs.append(PackageSuggestion(name=name, source=source))
        elif isinstance(p, dict):
            pkgs.append(PackageSuggestion(
                name        = p.get("name", "").strip(),
                source      = p.get("source", "official"),
                description = p.get("description", ""),
                reason      = p.get("reason", ""),
                alternates  = p.get("alternates", []),
            ))

    return SuggestionResult(
        packages  = pkgs,
        env_steps = data.get("env_steps", []),
        raw_goal  = goal,
    )
