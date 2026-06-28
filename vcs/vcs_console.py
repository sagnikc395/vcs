from __future__ import annotations

import sys
from typing import Literal

from rich.console import Console


ColorMode = Literal["auto", "always", "never"]


def console_for(color: ColorMode) -> Console:
    """Build a Rich console against the current stdout capture target."""
    return Console(
        file=sys.stdout,
        force_terminal=color == "always",
        no_color=color == "never",
        highlight=False,
        soft_wrap=True,
    )
