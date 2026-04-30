#!/usr/bin/env bash
set -euo pipefail

# Uninstall ai-pkg from pipx, yay, paru, or pip

echo "🧹 Uninstalling ai-pkg..."

# Try pipx uninstall
if command -v pipx &>/dev/null && pipx list | grep -q ai-pkg; then
    echo "Removing ai-pkg via pipx..."
    pipx uninstall ai-pkg || true
fi

# Try yay uninstall
if command -v yay &>/dev/null && yay -Q ai-pkg-bin &>/dev/null; then
    echo "Removing ai-pkg-bin via yay..."
    yay -Rns --noconfirm ai-pkg-bin || true
fi

# Try paru uninstall
if command -v paru &>/dev/null && paru -Q ai-pkg-bin &>/dev/null; then
    echo "Removing ai-pkg-bin via paru..."
    paru -Rns --noconfirm ai-pkg-bin || true
fi

# Try pip uninstall (editable/dev mode)
if python3 -m pip show ai-pkg &>/dev/null; then
    echo "Removing ai-pkg via pip..."
    python3 -m pip uninstall -y ai-pkg || true
fi

# Try local venv removal
if [ -d "$HOME/.local/ai-pkg" ]; then
    echo "Removing local venv at ~/.local/ai-pkg..."
    rm -rf "$HOME/.local/ai-pkg" || true
fi

if [ -f "$HOME/.local/bin/ai-pkg" ]; then
    echo "Removing shim at ~/.local/bin/ai-pkg..."
    rm -f "$HOME/.local/bin/ai-pkg" || true
fi

echo "✅ Uninstall complete."
