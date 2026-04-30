"""Base types for all AI backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class PackageSuggestion:
    name: str
    source: str = "official"           # "official" | "aur"
    description: str = ""
    reason: str = ""
    alternates: List[str] = field(default_factory=list)
    available: bool = True             # False = not found in repos


@dataclass
class SuggestionResult:
    packages: List[PackageSuggestion]
    env_steps: List[str]
    raw_goal: str
    error: str = ""                    # non-empty on failure


class AIBackend(ABC):
    @abstractmethod
    async def suggest(self, messages: List[dict[str, str]]) -> SuggestionResult: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def is_configured(self) -> bool: ...
