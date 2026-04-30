"""Fetch official documentation for packages from the Arch Wiki."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import urllib.parse
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_WIKI_API = "https://wiki.archlinux.org/api.php"
_TIMEOUT  = 8


async def _wiki_search(client: httpx.AsyncClient, query: str) -> Optional[str]:
    """Return the best matching Arch Wiki page title for a query."""
    try:
        r = await client.get(_WIKI_API, params={
            "action": "opensearch",
            "search": query,
            "limit":  3,
            "format": "json",
        }, timeout=_TIMEOUT)
        data = r.json()
        titles = data[1]
        return titles[0] if titles else None
    except Exception:
        return None


async def _wiki_extract(client: httpx.AsyncClient, title: str) -> Optional[str]:
    """Return a plain-text excerpt from an Arch Wiki page."""
    try:
        r = await client.get(_WIKI_API, params={
            "action":           "query",
            "titles":           title,
            "prop":             "extracts",
            "exintro":          "1",
            "exchars":          "2500",
            "exsectionformat":  "plain",
            "format":           "json",
        }, timeout=_TIMEOUT)
        data  = r.json()
        pages = data["query"]["pages"]
        page  = next(iter(pages.values()))
        html  = page.get("extract", "")
        # Strip HTML tags and collapse whitespace
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:2000] if text else None
    except Exception:
        return None


async def _fetch_one(client: httpx.AsyncClient, pkg_name: str) -> tuple[str, Optional[str]]:
    """Fetch the Arch Wiki snippet for a single package."""
    title = await _wiki_search(client, pkg_name)
    if not title:
        return pkg_name, None
    text = await _wiki_extract(client, title)
    return pkg_name, text


async def fetch_docs(packages: list) -> dict[str, str]:
    """
    Concurrently fetch Arch Wiki documentation for all packages.
    Returns a dict {pkg_name: wiki_excerpt}.
    """
    if not packages:
        return {}

    async with httpx.AsyncClient(
        headers={"User-Agent": "ai-pkg/1.0 (https://github.com/rohankrsingh/ai-pkg)"},
        follow_redirects=True,
    ) as client:
        results = await asyncio.gather(
            *[_fetch_one(client, p.name) for p in packages],
            return_exceptions=True,
        )

    docs: dict[str, str] = {}
    for entry in results:
        if isinstance(entry, tuple):
            name, text = entry
            if text:
                docs[name] = text
    return docs


def build_docs_context(docs: dict[str, str]) -> str:
    """Format fetched docs into a concise context block for the AI prompt."""
    if not docs:
        return ""
    parts = []
    for name, text in docs.items():
        parts.append(f"### {name}\n{text}")
    return "\n\n".join(parts)
