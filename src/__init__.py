"""Making a package."""

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

# pyrefly: ignore [missing-import]
from src.app import Application  # noqa: E402

__all__ = ["Application"]
