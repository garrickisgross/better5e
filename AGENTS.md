# AGENTS Instructions

## About the App
- Better 5e provides a small set of Pydantic models, a SQLite-backed data access
  layer, and a wizard engine for building tooling around the 5th Edition of the
  world's greatest roleplaying game.

## Architecture
- Use absolute imports without leading dots.
- Backend code changes must be explicitly called out in pull request
  descriptions.
- Main screen sections use the `Section` widget; dividers are removed and
  styling lives in the theme.
- `DAO.load_by_kind` skips invalid records so legacy entries without required
  fields do not crash the UI.
- `HomebrewPanel` requires the `App` instance so buttons can push creation pages
  directly.
- Homebrew creation pages use `SchemaFormBuilder` and `DropZone` for form
  generation and relations. Reuse these helpers for additional models.
- `SchemaFormBuilder.label_for()` exposes user-facing field labels; avoid using
  raw attribute names in UI forms.
- Use `ActionsEditor` for editing lists of Actions; it presents card widgets with
  optional `name`/`desc` fields and roll details.
- When forms grow, organize fields into a `QTabWidget` with sections like
  "Info", "Actions", "Modifier", and "Grants"; "Uses" inputs belong in the Info
  tab.
- Action cards appear above the add-action form and include a remove button for
  managing entries.
- Feature descriptions are required; submissions should be blocked when the
  description is empty.

## Style
- Page gutters are unified via `UI.style.tokens.gutter()` and used by the title
  bar and main screen layout.
- Maintain alignment between main screen sections; avoid spacer items that push
  sections apart and rely on stretches while keeping gutters consistent.
- The title bar's left margin is defined by `GUTTER` in `UI/shell/chrome.py`; keep
  this value in sync with `MainScreen` layout margins so the app title aligns with
  the dice panel.
- The app title uses a 12px text indent, a 2px top margin, and a bold 24px font
  so its left edge and baseline line up precisely with the dice options panel
  below.
- Main screen center uses a borderless scroll area named `CenterScroll` with
  `LeftPane`, `CenterPane`, and `RightPane` named for styling.
- Style `CenterScroll` by targeting its `qt_scrollarea_viewport` so child widgets
  like the "Create New" buttons keep their own borders and backgrounds.
- DiceOptionsPanel uses a 4×2 grid of dice buttons sized 88×44 with 10 px gutters.
  Modifier controls are centered with 40×40 ± buttons flanking a ~72 px number
  field.
- HomebrewPanel titles should use `SectionHeader` with its 'See All' button
  hidden for consistent styling.
- Action cards are styled as `Card` frames with a title (name), a subtitle for
  the action type, an optional body for the description, and the dice notation
  aligned to the right.
- Title bar action buttons (`WinBtnMin`, `WinBtnMax`, `WinBtnClose`) use a fixed
  size of 52×40 with ~2 px bottom padding to center the glyphs. Keep these
  dimensions in sync with `TitleBar.HEIGHT` so the buttons align with the app
  title.

## Testing
- Run tests with coverage using:
  `pytest --maxfail=1 --disable-warnings -q --cov=better5e`
- Coverage artifacts (e.g. `.coverage`) are ignored and should not be committed.
- All test runs must pass and achieve 100% coverage before pushing changes.

