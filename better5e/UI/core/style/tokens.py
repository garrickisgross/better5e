"""Design tokens for the better5e UI.

Provides color, spacing, radius and typography values used throughout
application styling. Tokens are returned as plain dictionaries to keep the
API simple and easily serialisable.  The :func:`dark` function exposes the
primary dark theme palette while :func:`light` offers a lighter alternative
for future expansion.
"""

from __future__ import annotations

from typing import Any, Dict


def _base() -> Dict[str, Any]:
    """Return shared tokens across themes."""

    return {
        # Radii
        "radius_sm": 6,
        "radius_md": 10,
        "radius_lg": 16,
        # Spacing scale
        "space_xs": 4,
        "space_sm": 8,
        "space_md": 12,
        "space_lg": 16,
        "space_xl": 24,
        # Typography
        "font_family": "Segoe UI, Roboto, Inter, Helvetica Neue, Arial",
        "font_mono": "JetBrains Mono, Consolas, Menlo, monospace",
    }


def dark() -> Dict[str, Any]:
    """Return tokens for the dark theme."""

    t = _base()
    t.update(
        {
            "bg": "#0f1115",
            "surface": "#161a22",
            "surfaceAlt": "#1c2230",
            "text": "#e5e7eb",
            "mutedText": "#9aa3b2",
            "border": "#2a3242",
            "accent": "#7c3aed",
            "accentHover": "#8b5cf6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
        }
    )
    return t


def gutter() -> int:
    """Return the standard horizontal page padding."""

    return 20


def light() -> Dict[str, Any]:
    """Return tokens for a light theme.

    The palette mirrors :func:`dark` but with light surfaces.  This function is
    primarily for completeness; the application defaults to the dark theme.
    """

    t = _base()
    t.update(
        {
            "bg": "#ffffff",
            "surface": "#f3f4f6",
            "surfaceAlt": "#e5e7eb",
            "text": "#111827",
            "mutedText": "#6b7280",
            "border": "#d1d5db",
            "accent": "#7c3aed",
            "accentHover": "#8b5cf6",
            "success": "#059669",
            "warning": "#d97706",
            "error": "#dc2626",
        }
    )
    return t
