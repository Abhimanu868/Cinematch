"""Utility helper functions."""

from datetime import datetime


def format_runtime(minutes: int | None) -> str:
    """Format runtime in minutes to 'Xh Ym' format."""
    if not minutes:
        return "N/A"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def truncate_text(text: str | None, max_length: int = 200) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."
