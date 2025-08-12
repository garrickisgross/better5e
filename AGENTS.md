# AGENTS Instructions

- Use absolute imports without leading dots.
- Run tests with coverage using:
  `pytest --maxfail=1 --disable-warnings -q --cov=better5e`
- Coverage artifacts (e.g. `.coverage`) are ignored and should not be committed.
- Main screen sections use the `Section` widget; dividers are removed and styling lives in the theme.
- Page gutters are unified via `UI.style.tokens.gutter()` and used by the title bar and main screen layout.
- Main screen center uses a borderless scroll area named `CenterScroll` with `LeftPane`, `CenterPane`, and `RightPane` named for styling.
- Style `CenterScroll` by targeting its `qt_scrollarea_viewport` so child widgets like the "Create New" buttons keep their own borders and backgrounds.
- DiceOptionsPanel centers its dice grid and modifier control; dice buttons are fixed at 60px wide with 8px gutters. ModifierControl uses wide ± buttons and a ~40px number field to keep controls compact.
- Center column spacing between sections is 18px with 8px padding at the top and bottom; avoid spacer items that create large gaps.

