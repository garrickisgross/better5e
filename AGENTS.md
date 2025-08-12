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
- DiceOptionsPanel uses a 4×2 grid of dice buttons sized 88×44 with 10 px gutters. Modifier controls are centered with 40×40 ± buttons flanking a ~72 px number field.
- HomebrewPanel titles should use `SectionHeader` with its 'See All' button hidden for consistent styling.

- Homebrew creation pages use `SchemaFormBuilder` and `DropZone` for form generation and relations. Reuse these helpers for additional models.
- `HomebrewPanel` requires the `App` instance so buttons can push creation pages directly.
- `SchemaFormBuilder.label_for()` exposes user-facing field labels; avoid using raw attribute names in UI forms.
- Use `ActionsEditor` for editing lists of Actions (action type and roll) when building new homebrew pages.

