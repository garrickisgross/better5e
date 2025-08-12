# AGENTS Instructions

- Use absolute imports without leading dots.
- Run tests with coverage using:
  `pytest --maxfail=1 --disable-warnings -q --cov=better5e`
- Coverage artifacts (e.g. `.coverage`) are ignored and should not be committed.
- Main screen sections use the `Section` widget; dividers are removed and styling lives in the theme.
- Page gutters are unified via `UI.style.tokens.gutter()` and used by the title bar and main screen layout.
- The title bar's left margin is defined by `GUTTER` in `UI/shell/chrome.py`; keep this value in sync with `MainScreen` layout margins so the app title aligns with the dice panel.
- The app title uses a 12px text indent, a 2px top margin, and a bold 24px font so its left edge and baseline line up precisely with the dice options panel below.
- Main screen center uses a borderless scroll area named `CenterScroll` with `LeftPane`, `CenterPane`, and `RightPane` named for styling.
- Style `CenterScroll` by targeting its `qt_scrollarea_viewport` so child widgets like the "Create New" buttons keep their own borders and backgrounds.
- DiceOptionsPanel centers its dice grid and modifier control; dice buttons are fixed at 60px wide with 8px gutters. ModifierControl uses wide ± buttons and a ~40px number field to keep controls compact.

