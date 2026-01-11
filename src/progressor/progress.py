"""
Main progress bar implementation.
Enhanced with themes, colors, and custom templates.
Minimal dependencies, no external libraries needed.
"""

import sys
import time
from typing import Callable, Optional, Union, List, Tuple

# Import new modules
from .colors import ColorTheme
from .themes import UnicodeBlocks, GeometricSymbols


class ProgressStyle:
    """Predefined progress bar styles (expanded)"""
    
    # Block styles
    BLOCK = "block"             # ████████░░░░░░░░
    CLASSIC = "classic"         # [■■■■■■■■□□□□□□□□]
    BRAILLE = "braille"         # ⣿⣿⣿⣿⣀⣀⣀⣀
    ARROW = "arrow"             # >>>>>>>>--------
    EQUAL = "equal"             # =========-------
    DOT = "dot"                 # ••••••••........
    
    # Spinners
    SPIN_SIMPLE = "spin_simple" # |/-\\|/-\...
    SPIN_DOTS = "spin_dots"     # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏
    SPIN_ARROW = "spin_arrow"   # ←↖↑↗→↘↓↙
    
    # New styles
    VERTICAL = "vertical"       # ▁▂▃▄▅▆▇█ (vertical blocks)
    CIRCLE = "circle"           # ○◔◑◕●
    SQUARE = "square"           # □◱◲■
    GRADIENT = "gradient"       # ░▒▓█ (shaded gradient)
    HASH = "hash"               # #####.....
    STAR = "star"               # ★★★★★☆☆☆☆☆
    TRIANGLE = "triangle"       # ▲▲▲▲▽▽▽▽
    BOUNCE = "bounce"           # (→    ) ( →   ) etc.


def get_progress_drawer(
    style: Union[str, List[str]] = "block",
    width: int = 30,
    show_percentage: bool = True,
    show_counter: bool = False,
    show_eta: bool = False,
    show_speed: bool = False,  # NEW: Show operations per second
    spinner_only: bool = False,
    color_theme: Optional[Union[str, Callable]] = None,
    custom_chars: Optional[Tuple[str, str]] = None
) -> Callable[[float, Optional[int], Optional[float], Optional[float]], None]:
    """
    Factory that returns a progress drawing function with selected style.
    
    Enhanced with color support and custom character sets.
    
    The returned function signature:
        def draw(progress: float, current: int | None = None, 
                eta: float | None = None, speed: float | None = None) -> None:
            # progress ∈ [0,1]
            # speed: operations per second (if show_speed=True)
    """

    # Track start time for speed calculation
    start_time = time.time()
    last_update = start_time
    last_value = 0
    
    # Determine style and handle custom inputs
    style_name = ""
    filled_char = ""
    empty_char = ""
    chars = []
    
    if custom_chars is not None:
        # User provided custom characters like ("@", ".")
        filled_char, empty_char = custom_chars
        style_name = "custom"
    elif isinstance(style, list):
        # User provided a list of characters for progressive fill
        chars = style
        if len(chars) < 1:
            raise ValueError("Character list must have at least one character")
        style_name = "custom_list"
    else:
        # Regular style name
        style_name = style.lower()
    
    # Map style names to drawing functions
    if style_name == "block":
        chars = " ▏▎▍▋▊▉"
        def draw_func(p: float):
            filled = int(p * (width * len(chars)-1))
            full = filled // (len(chars)-1)
            part = filled % (len(chars)-1)
            bar = chars[-1] * full + (chars[part] if part else "")
            bar += " " * (width - len(bar))
            return bar, " " * width

    elif style_name == "classic":
        def draw_func(p: float):
            filled = int(p * width)
            return "■" * filled, "□" * (width - filled)

    elif style_name == "braille":
        braille = " ⡀⡄⡆⡇⡏⡟⡿⣿"
        def draw_func(p: float):
            filled = int(p * width * 4)
            full = filled // 4
            part = filled % 4
            bar = braille[7] * full + (braille[part] if part else "")
            bar += " " * (width - len(bar))
            return bar, " " * width

    elif style_name == "arrow":
        def draw_func(p: float):
            filled = int(p * width)
            return ">" * filled, "-" * (width - filled)

    elif style_name == "equal":
        def draw_func(p: float):
            filled = int(p * width)
            return "=" * filled, "-" * (width - filled)

    elif style_name == "dot":
        def draw_func(p: float):
            filled = int(p * width)
            return "•" * filled, "." * (width - filled)

    elif style_name == "vertical":
        vertical_chars = UnicodeBlocks.VERTICAL
        def draw_func(p: float):
            filled = int(p * width)
            bar = ""
            for i in range(width):
                if i < filled:
                    # Use different heights based on position
                    height_idx = min(int(p * len(vertical_chars)), len(vertical_chars)-1)
                    bar += vertical_chars[height_idx]
                else:
                    bar += " "
            return bar, " " * width

    elif style_name == "circle":
        circle_chars = GeometricSymbols.CIRCLES["filled"]
        def draw_func(p: float):
            filled = int(p * width)
            filled_part = ""
            for i in range(filled):
                # Progressively fill circles
                idx = min(int(p * len(circle_chars)), len(circle_chars)-1)
                filled_part += circle_chars[idx]
            empty_part = circle_chars[0] * (width - filled)
            return filled_part, empty_part

    elif style_name == "square":
        square_chars = GeometricSymbols.SQUARES
        def draw_func(p: float):
            filled = int(p * width)
            filled_part = ""
            for i in range(filled):
                # Progressively fill squares
                idx = min(int(p * len(square_chars)), len(square_chars)-1)
                filled_part += square_chars[idx]
            empty_part = square_chars[0] * (width - filled)
            return filled_part, empty_part

    elif style_name == "gradient":
        def draw_func(p: float):
            filled = int(p * width)
            bar = ""
            for i in range(width):
                if i < filled:
                    # More filled = darker shade
                    if p < 0.33:
                        bar += "░"
                    elif p < 0.66:
                        bar += "▒"
                    else:
                        bar += "▓"
                else:
                    bar += " "
            return bar, " " * width

    elif style_name == "hash":
        def draw_func(p: float):
            filled = int(p * width)
            return "#" * filled, "." * (width - filled)

    elif style_name == "star":
        def draw_func(p: float):
            filled = int(p * width)
            return "★" * filled, "☆" * (width - filled)

    elif style_name == "triangle":
        def draw_func(p: float):
            filled = int(p * width)
            return "▲" * filled, "▽" * (width - filled)

    elif style_name == "bounce":
        frames = ["(→    )", "( →   )", "(  →  )", "(   → )", "(    →)", 
                 "(   ← )", "(  ←  )", "( ←   )", "(←    )"]
        def make_bounce():
            i = 0
            def bounce(p: float):
                nonlocal i
                # Scale frame based on progress
                frame_idx = int(p * (len(frames) - 1))
                s = frames[frame_idx]
                i = (i + 1) % len(frames)
                return s, ""
            return bounce
        
        draw_func = make_bounce()

    elif style_name == "spin_arrow":
        frames = ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]
        def make_spinner():
            i = 0
            def spin(_: float):
                nonlocal i
                s = frames[i % len(frames)]
                i = (i + 1) % len(frames)
                return s * (width // 3) if spinner_only else s, ""
            return spin
        
        draw_func = make_spinner()

    elif style_name in ("spin_simple", "spin_dots"):
        if style_name == "spin_simple":
            frames = r"\|/-"
        else:
            frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

        def make_spinner():
            i = 0
            def spin(_: float):
                nonlocal i
                s = frames[i % len(frames)]
                i = (i + 1) % len(frames)
                return s * (width // 3) if spinner_only else s, ""
            return spin
        
        draw_func = make_spinner()

    elif style_name == "custom":
        # Custom characters from user (filled_char, empty_char)
        def draw_func(p: float):
            filled = int(p * width)
            return filled_char * filled, empty_char * (width - filled)

    elif style_name == "custom_list":
        # List of characters for progressive fill
        if len(chars) == 0:
            raise ValueError("Character list cannot be empty")
        def draw_func(p: float):
            filled = int(p * width)
            filled_part = ""
            for i in range(filled):
                # Use character based on position in sequence
                idx = min(int(p * len(chars)), len(chars)-1)
                filled_part += chars[idx]
            empty_part = chars[0] * (width - filled)
            return filled_part, empty_part

    else:
        raise ValueError(f"Unknown style: {style!r}. Available: {', '.join([k for k in ProgressStyle.__dict__.keys() if not k.startswith('_')])}")

    # Color theme handler
    if color_theme is None:
        color_handler = ColorTheme.default
    elif callable(color_theme):
        color_handler = color_theme
    elif color_theme == "green_red":
        color_handler = ColorTheme.green_red
    elif color_theme == "blue_yellow":
        color_handler = ColorTheme.blue_yellow
    elif color_theme == "gradient":
        color_handler = ColorTheme.gradient
    elif color_theme == "rainbow":
        color_handler = ColorTheme.rainbow
    elif color_theme == "monochrome":
        color_handler = ColorTheme.monochrome
    elif color_theme == "terminal":
        color_handler = ColorTheme.terminal
    else:
        color_handler = ColorTheme.default

    def draw(
        progress: float,
        current: Optional[int] = None,
        eta: Optional[float] = None,
        speed: Optional[float] = None
    ):
        """
        Draw progress bar according to selected style
        
        Args:
            progress: 0..1
            current: Current item count (if show_counter=True)
            eta: Estimated time remaining in seconds (if show_eta=True)
            speed: Operations per second (if show_speed=True)
        """
        # Fix variable scope issue
        nonlocal last_update, last_value
        
        if not 0 <= progress <= 1:
            progress = max(0, min(1, progress))
        
        # Calculate speed if not provided but requested
        computed_speed = None
        if show_speed and speed is None and current is not None:
            now = time.time()
            if now > last_update:
                computed_speed = (current - last_value) / (now - last_update)
                last_update = now
                last_value = current
        
        # Draw the bar
        filled_part, empty_part = draw_func(progress)
        
        # Apply color theme
        if color_handler:
            filled_part, empty_part = color_handler(filled_part, empty_part, progress)
        
        bar = filled_part + empty_part
        
        # Build info parts
        parts = []
        
        if show_percentage:
            parts.append(f"{progress:5.1%}")
        
        if show_counter and current is not None:
            parts.append(f"{current:,}")
        
        if show_eta and eta is not None and eta > 0:
            if eta < 60:
                parts.append(f"ETA {eta:.1f}s")
            elif eta < 3600:
                parts.append(f"ETA {eta/60:.1f}m")
            else:
                parts.append(f"ETA {eta/3600:.1f}h")
        
        if show_speed:
            speed_to_show = speed if speed is not None else computed_speed
            if speed_to_show is not None:
                if speed_to_show < 1000:
                    parts.append(f"{speed_to_show:.1f}/s")
                elif speed_to_show < 1_000_000:
                    parts.append(f"{speed_to_show/1000:.1f}K/s")
                else:
                    parts.append(f"{speed_to_show/1_000_000:.1f}M/s")
        
        extra = " │ " + "  ".join(parts) if parts else ""
        
        line = f"\r{bar}{extra}"
        sys.stdout.write(line)
        sys.stdout.flush()
        
        # Print newline when complete
        if progress >= 1:
            sys.stdout.write("\n")
            sys.stdout.flush()

    return draw


# Multi-bar display (simple implementation)
class MultiProgress:
    """
    Simple multi-progress bar display.
    Useful for tracking multiple concurrent processes.
    """
    
    def __init__(self, count: int, style: str = "block", width: int = 30):
        self.count = count
        self.drawers = [get_progress_drawer(style, width, show_percentage=False) 
                       for _ in range(count)]
        self.lines_written = 0
    
    def update(self, index: int, progress: float, label: str = ""):
        """Update a specific progress bar"""
        if index < 0 or index >= self.count:
            raise IndexError(f"Index {index} out of range (0-{self.count-1})")
        
        # Move cursor to the right line
        if self.lines_written:
            sys.stdout.write(f"\033[{self.lines_written}A")  # Move up
        
        # Update all bars
        for i in range(self.count):
            if i == index:
                prefix = f"{label}: " if label else f"Bar {i+1}: "
                sys.stdout.write(prefix)
                self.drawers[i](progress)
                sys.stdout.write("\n")
            else:
                # Just keep existing line
                sys.stdout.write("\n")
        
        self.lines_written = self.count
        sys.stdout.flush()
    
    def complete(self):
        """Complete all progress bars"""
        sys.stdout.write("\n" * self.lines_written)
        sys.stdout.flush()
