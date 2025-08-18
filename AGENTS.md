# Agents.md

> **Purpose**: This document tells Codex how to work inside the **Better5e** repository—what the project is, how to make changes safely, what patterns to follow, and the quality bar for a mergeable PR.

Better5e provides a small set of **Pydantic** models, a **SQLite**-backed data access layer, and a **PyQt6** frontend for homebrewing characters and campaigns for the 5th Edition of the world’s greatest role-playing game.

---

## Production expectations

Better5e is intended to be a **production-grade desktop application**. Code should be written with maintainability, testability, and stability in mind. UI components must feel polished and consistent with professional-grade software. Avoid quick hacks—prefer patterns that scale, with attention to accessibility, responsiveness, and cross-platform behavior.

## 1) What you’re building

- A **data-driven** 5e toolkit: users define custom **Features**, **Items**, **Spells**, **Classes/Subclasses**, **Modifiers**, and **Rollables** that flow through a rules engine.
- A **desktop UI** in PyQt6 for browsing, creating, and editing homebrew content.
- A **simple DAO** over SQLite for persistence.

**Key goals:** correctness of rules interactions, predictable persistence, crisp UI patterns, and maintainable code.

---

## 2) How Codex should work here

1. **Prefer small, incremental PRs** with focused scope.
2. **Follow the patterns described below** (architecture, UI, DAO, testing).
3. **If a change requires backend model/DAO updates**, call this out explicitly in the PR description under “Backend changes”.
4. **Preserve public API compatibility** unless the task explicitly authorizes a breaking change—when breaking, include automated migrations or backward-compatible shims.
5. **Ship tests** for all new logic and regressions; keep coverage at the project target.
6. **Keep UI consistent** by reusing shared widgets, builders, and tokens.

---

## 3) Tech stack & project shape

- **Language**: Python 3.x
- **Frontend**: PyQt6
- **Models**: Pydantic
- **Storage**: SQLite (DAO abstraction)
- **Testing**: `pytest` + coverage
- **Style**: repo theme + shared widgets (e.g., `Section`, `Card`, `SchemaFormBuilder`, `DropZone`, `ActionsEditor`)

---

## 4) Architecture guidelines

- **Imports**: Use **absolute imports** (no leading dots).
- **Separation of concerns**:
  - **Models**: Pydantic classes, validation, and serialization boundaries.
  - **DAO**: CRUD + query helpers; models in, JSON payloads in the table as needed; no UI logic.
  - **UI**: Only presentation + user interaction; use builder helpers for forms and list editors.
- **Persistence safety**:
  - DAO APIs **must not** raise on legacy/invalid rows; **skip or sanitize** and log.
  - Provide **idempotent** migrations where schema changes are required.
- **Error handling**: Fail fast on programmer errors (tests catch these); degrade gracefully on user data.

---

## 5) UI/UX patterns to reuse

- **Main screen sections**: Use the `Section` widget; **styling lives in the theme** (do not add per-instance borders/dividers).
- **Scrollable center**: Use `CenterScroll` with named panes (`LeftPane`, `CenterPane`, `RightPane`) for stylesheet targeting.
- **Homebrew creation**: Use `SchemaFormBuilder` for forms and `DropZone` for relations (drag-and-drop of related objects).
- **Action lists**: Use `ActionsEditor` cards above the add form; include remove buttons; support optional `name`/`desc` and roll details.
- **Growing forms**: Organize with `QTabWidget` sections like **Info**, **Actions**, **Modifiers**, **Grants**. Place “Uses” inputs in **Info**.
- **Placeholders**: It’s acceptable for some UI buttons to be placeholders if a task says so—make this explicit in PR notes.

**Form labeling**: Use `SchemaFormBuilder.label_for()` (no raw attribute names in user-facing labels).

### UI polish guidelines

- **Consistency**: Always reuse shared widgets/components rather than creating ad-hoc variants.
- **Accessibility**: Ensure contrast ratios, font sizes, and interactive areas are large enough to be usable across devices.
- **Responsiveness**: Layouts should adapt gracefully to window resizing. Avoid clipped or overlapping content.
- **Feedback**: Provide clear visual feedback (hover, active, disabled states) for all interactive elements.
- **Error handling**: Show user-friendly error states/messages rather than crashing or silently failing.
- **Professional feel**: Avoid placeholder or debug text in production UI. Use concise, user-facing copy.
- **Performance**: Avoid unnecessary re-renders or blocking operations on the UI thread; keep the app smooth.

---

## 6) Data & DAO rules

- **Pydantic first**: Validation on model boundaries; store canonical JSON payloads where applicable.
- **DAO.load_by_kind** must **skip invalid rows** and continue (legacy tolerance).
- **Round-trip fidelity**: Anything loaded should be savable without mutation (unless a migration updates it deterministically).
- **IDs**: Use UUIDs for identity; surface relations as UUIDs in storage and resolve in the UI via drag-and-drop where appropriate.

---

## 7) Coding style & layout

- **Gutters & spacing**: Use `UI.style.tokens.gutter()` for consistent spacing. Keep title bar and main layout margins synchronized.
- **Title bar**: `GUTTER` in `UI/shell/chrome.py` must align with `MainScreen` margins. Button sizes must remain in sync with `TitleBar.HEIGHT`.
- **Dice panel**: Keep grid/gutter sizing consistent (see Appendix for current values).
- **No ad-hoc styling** in widgets; prefer named widgets and theme targeting.

---

## 8) Testing & quality

- **Command**:
  ```bash
  pytest --maxfail=1 --disable-warnings -q --cov=better5e
  ```
- **Coverage artifacts** (e.g., `.coverage`) are ignored—do not commit.
- **Quality bar**: All tests must pass; target **100% coverage** for touched modules. At minimum, tests must cover:
  - New branches/conditions introduced by the PR
  - DAO behaviors for invalid/legacy rows (skip semantics)
  - UI builders (form field mapping, required/disabled states)
  - Serialization round-trips for changed models

**Golden rule**: If you fix a bug, add a test that fails before the fix and passes after.

---

## 9) Pull requests: structure & checklists

**PR template (paste into description):**
```markdown
## Summary
<short, outcome-focused description>

## Scope
- [ ] Models
- [ ] DAO
- [ ] UI
- [ ] Tests
- [ ] Docs (Agents.md/README/UI guide)

## Backend changes
<explicitly list any model/DAO/schema changes or write "None">

## User-facing changes
<screenshots or a short demo description>

## Risks & mitigations
<compat, migrations, legacy data handling>

## Validation
- [ ] New/updated unit tests
- [ ] Manual smoke (load/create/edit/save)
- [ ] Legacy data path exercised (invalid records skipped)
```

**Definition of Done**
- Reused shared widgets/builders (no bespoke clones).
- No regressions in layout alignment/gutters.
- DAO tolerant to legacy/invalid rows; UI remains responsive.
- Tests added and coverage target met.
- PR description explicitly states backend changes (or none).

---

## 10) Task playbook (what to do for common asks)

**A) Add a new homebrew model**
1. Define/extend **Pydantic** model with validation.
2. Add DAO persistence + queries (round-trip).
3. Add **SchemaFormBuilder** mapping + `label_for` entries.
4. Implement **DropZone** for relations if needed.
5. Add **ActionsEditor** if the model includes actions.
6. Add tests: model validation, DAO round-trip, builder mapping.

**B) Extend an existing form**
1. Add the field to the model (with default/validation).
2. Map to builder with label; place in correct **QTabWidget** section.
3. Update tests for required/optional logic and serialization.

**C) Tolerate legacy data**
1. Ensure `DAO.load_by_kind` **skips** invalid rows and logs.
2. Consider a small migration or auto-fix if safe and deterministic.
3. Add a test that loads a bad record and confirms the UI doesn’t crash.

**D) New list editor behavior**
1. Extend `ActionsEditor`/shared component instead of duplicating.
2. Expose small, composable hooks (e.g., `on_add`, `on_remove`).
3. Test the behavior and UI state transitions.

---

## 11) Local development

- **Run tests**: see Section 8.
- **Run the app**: use the repo’s documented entrypoint (keep CLI/UI launch scripts in sync with README).
- **Style**: rely on the project’s theme; do not embed colors/margins ad-hoc.

---

## 12) When to ask vs. decide

- **Ask** (leave a PR note) when:
  - A change would **break** public model fields or DAO schemas.
  - UI patterns require a **new shared component** rather than extending an existing one.
  - A migration may drop or rewrite user data.

- **Decide** (and document in PR) when:
  - Adding non-breaking fields with sane defaults.
  - Wiring new forms through `SchemaFormBuilder`/`DropZone`.
  - Improving tests, coverage, or internal refactors without API change.

---

## 13) Glossary

- **SchemaFormBuilder**: Maps Pydantic fields → labeled UI form fields; provides `label_for`.
- **DropZone**: Drag-and-drop widget for attaching related objects (by UUID behind the scenes).
- **ActionsEditor**: Card-based editor for a list of in-game actions (name/desc/rolls, with remove).
- **Section / Card**: Standard containers for visual consistency.

---

## Appendix: Current implementation notes (stable until replaced)

> These reflect the present codebase and should be followed to maintain consistency. If you must diverge, justify in the PR.

### Architecture
- Backend code changes must be **explicitly** called out in PR descriptions.
- `DAO.load_by_kind` **skips invalid records** so legacy entries without required fields do not crash the UI.
- `HomebrewPanel` may display **placeholder** buttons not wired to actions.
- Homebrew creation pages use **`SchemaFormBuilder`** and **`DropZone`** for form generation and relations; **reuse these helpers** for additional models.
- `SchemaFormBuilder.label_for()` exposes user-facing field labels; **avoid raw attribute names** in UI forms.
- Use **`ActionsEditor`** for editing lists of Actions; it presents card widgets with optional `name`/`desc` and roll details.
- When forms grow, organize fields into a **`QTabWidget`** with sections like **Info**, **Actions**, **Modifier**, and **Grants**; **“Uses”** inputs belong in the **Info** tab.
- Action cards appear **above** the add-action form and include a remove button.
- **Feature descriptions are required**; submissions should be blocked when the description is empty.

### Style
- Page gutters are unified via `UI.style.tokens.gutter()` and used by the title bar and main layout.
- Maintain **alignment** between main screen sections; avoid spacer items that push sections apart—use stretches with consistent gutters.
- The title bar’s left margin is defined by **`GUTTER`** in `UI/shell/chrome.py`; keep this in sync with `MainScreen` margins so the app title aligns with the dice panel.
- The app title uses a **12px text indent**, **2px top margin**, and **bold 24px font** so its left edge and baseline align with the dice options panel.
- The main screen center uses a **borderless** scroll area named `CenterScroll` with `LeftPane`, `CenterPane`, `RightPane` for styling.
- Style `CenterScroll` by targeting its `qt_scrollarea_viewport` so child widgets like “Create New” buttons keep their own borders/backgrounds.
- DiceOptionsPanel: **4×2** grid of dice buttons sized **88×44** with **10px** gutters. Modifier controls centered with **40×40** ± buttons flanking a ~**72px** number field.
- HomebrewPanel titles should use **`SectionHeader`** with its “See All” button **hidden** for consistency.
- Title bar action buttons (`WinBtnMin`, `WinBtnMax`, `WinBtnClose`) use **52×40** with ~**2px** bottom padding; keep in sync with `TitleBar.HEIGHT`.

### Testing
- Run tests with coverage:
  ```bash
  pytest --maxfail=1 --disable-warnings -q --cov=better5e
  ```
- Coverage artifacts (e.g., `.coverage`) are ignored and should not be committed.
- All test runs must pass and achieve **100% coverage for touched code** before pushing.

---

**TL;DR for Codex**: Reuse the shared builders, keep DAO tolerant to old data, align with the theme, call out backend changes in PRs, and ship tests that prove it all works.
