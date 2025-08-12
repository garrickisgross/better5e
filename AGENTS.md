# AGENTS Instructions

- Use absolute imports without leading dots.
- Run tests with coverage using:
  `pytest --maxfail=1 --disable-warnings -q --cov=better5e`
- Coverage artifacts (e.g. `.coverage`) are ignored and should not be committed.
- Main screen sections use the `Section` widget; dividers are removed and styling lives in the theme.
- Page gutters are unified via `UI.style.tokens.gutter()` and used by the title bar and main screen layout.
- Main screen center uses a borderless scroll area named `CenterScroll` with `LeftPane`, `CenterPane`, and `RightPane` named for styling.
- Style `CenterScroll` by targeting its `qt_scrollarea_viewport` so child widgets like the "Create New" buttons keep their own borders and backgrounds.
- DiceOptionsPanel uses a 4×2 grid of dice buttons sized 88×44 with 10 px gutters. Modifier controls are centered with 40×40 ± buttons flanking a ~72 px number field.

