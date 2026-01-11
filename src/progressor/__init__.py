"""
progressor-lib - Enhanced progress bars with themes, colors, and custom templates.
Minimal dependencies, no external libraries needed.
"""

from .progress import get_progress_drawer, ProgressStyle, MultiProgress
from .colors import Colors, ColorTheme, apply_color
from .themes import (
    UnicodeBlocks, GeometricSymbols, EmojiThemes,
    ASCIIArt, FancySymbols, CustomTemplate
)

__version__ = "1.0.0"
__all__ = [
    "get_progress_drawer",
    "ProgressStyle",
    "MultiProgress",
    "Colors",
    "ColorTheme",
    "apply_color",
    "UnicodeBlocks",
    "GeometricSymbols",
    "EmojiThemes",
    "ASCIIArt",
    "FancySymbols",
    "CustomTemplate",
    "__version__"
]
