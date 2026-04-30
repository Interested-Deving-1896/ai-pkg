from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from . import __version__

console = Console()

BANNER_ART = r"""
 █████╗ ██╗      ██████╗ ██╗  ██╗ ██████╗ 
██╔══██╗██║      ██╔══██╗██║ ██╔╝██╔════╝ 
███████║██║█████╗██████╔╝█████╔╝ ██║  ███╗
██╔══██║██║╚════╝██╔═══╝ ██╔═██╗ ██║   ██║
██║  ██║██║      ██║     ██║  ██╗╚██████╔╝
╚═╝  ╚═╝╚═╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝ 
"""

def show_banner():
    """Show the banner using a Gemini-inspired color scheme."""
    art = Text()
    
    # Gradient-like Gemini colors (cyan -> blue -> purple)
    lines = BANNER_ART.splitlines()
    colors = [
        "#5DADE2",
        "#4A90E2",
        "#6C8CD5",
        "#8E6CCF",
        "#B565A7",
    ]
    
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        art.append(line + "\n", style=f"bold {color}")
        
    art.append("\nAI Package Wizard for Arch Linux\n", style="bold italic bright_black")
    
    panel = Panel(
        Align.center(art),
        border_style="blue_violet",
        expand=False,
    )
    
    console.print(panel)
