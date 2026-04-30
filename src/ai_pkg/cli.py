"""ai-pkg CLI entry point."""
import sys

from . import __version__
from .tui import run_tui

def main() -> None:
    args = sys.argv[1:]

    if "--version" in args or "-v" in args:
        print(f"ai-pkg {__version__}")
        sys.exit(0)

    if "--help" in args or "-h" in args:
        print("Usage: ai-pkg")
        print("       (Starts the interactive AI Package Wizard)")
        sys.exit(0)

    # The Textual TUI is the primary interface now
    run_tui()

if __name__ == "__main__":
    main()