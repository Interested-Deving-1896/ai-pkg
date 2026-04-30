"""Persistent configuration for ai-pkg stored at ~/.config/ai-pkg/config.toml."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib  # stdlib Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

CONFIG_DIR = Path.home() / ".config" / "ai-pkg"
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class AIConfig:
    model: str = "gemini"          # gemini | openai | groq | ollama
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"


@dataclass
class PkgConfig:
    aur_helper: str = "yay"        # yay | paru
    auto_yes: bool = False


@dataclass
class Config:
    ai: AIConfig = field(default_factory=AIConfig)
    pkg: PkgConfig = field(default_factory=PkgConfig)


# ── Serialization ────────────────────────────────────────────────────────────

def _b(v: bool) -> str:
    return "true" if v else "false"


def _serialize(config: Config) -> str:
    ai, pkg = config.ai, config.pkg
    return (
        "[ai]\n"
        f'model = "{ai.model}"\n'
        f'gemini_api_key = "{ai.gemini_api_key}"\n'
        f'gemini_model = "{ai.gemini_model}"\n'
        f'openai_api_key = "{ai.openai_api_key}"\n'
        f'openai_model = "{ai.openai_model}"\n'
        f'openai_base_url = "{ai.openai_base_url}"\n'
        f'groq_api_key = "{ai.groq_api_key}"\n'
        f'groq_model = "{ai.groq_model}"\n'
        f'ollama_base_url = "{ai.ollama_base_url}"\n'
        f'ollama_model = "{ai.ollama_model}"\n'
        "\n"
        "[pkg]\n"
        f'aur_helper = "{pkg.aur_helper}"\n'
        f'auto_yes = {_b(pkg.auto_yes)}\n'
    )


# ── Public API ────────────────────────────────────────────────────────────────

def load_config() -> Config:
    """Load config from file; ENV vars always override."""
    config = Config()

    if CONFIG_FILE.exists() and tomllib is not None:
        try:
            with open(CONFIG_FILE, "rb") as fh:
                data = tomllib.load(fh)
            ai_d = data.get("ai", {})
            pkg_d = data.get("pkg", {})
            config.ai = AIConfig(
                model=ai_d.get("model", config.ai.model),
                gemini_api_key=ai_d.get("gemini_api_key", ""),
                gemini_model=ai_d.get("gemini_model", config.ai.gemini_model),
                openai_api_key=ai_d.get("openai_api_key", ""),
                openai_model=ai_d.get("openai_model", config.ai.openai_model),
                openai_base_url=ai_d.get("openai_base_url", config.ai.openai_base_url),
                groq_api_key=ai_d.get("groq_api_key", ""),
                groq_model=ai_d.get("groq_model", config.ai.groq_model),
                ollama_base_url=ai_d.get("ollama_base_url", config.ai.ollama_base_url),
                ollama_model=ai_d.get("ollama_model", config.ai.ollama_model),
            )
            config.pkg = PkgConfig(
                aur_helper=pkg_d.get("aur_helper", config.pkg.aur_helper),
                auto_yes=pkg_d.get("auto_yes", config.pkg.auto_yes),
            )
        except Exception:
            pass  # fall back to defaults on any parse error

    # ENV overrides (highest priority)
    _env_map = [
        ("GEMINI_API_KEY", "ai", "gemini_api_key"),
        ("OPENAI_API_KEY", "ai", "openai_api_key"),
        ("GROQ_API_KEY", "ai", "groq_api_key"),
        ("AI_PKG_AUR_HELPER", "pkg", "aur_helper"),
    ]
    for env_var, section, attr in _env_map:
        val = os.environ.get(env_var)
        if val:
            setattr(getattr(config, section), attr, val)

    return config


def save_config(config: Config) -> None:
    """Persist config to ~/.config/ai-pkg/config.toml."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(_serialize(config), encoding="utf-8")
