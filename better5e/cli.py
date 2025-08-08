from __future__ import annotations

"""Simple command line interface for the :mod:`better5e` package.

The CLI is intentionally lightweight and primarily exists so that the backend
flows can be validated before a graphical front end is implemented.  Only a
subset of the wizard's capabilities are exposed but the design mirrors what a
full featured client would do which keeps the interface useful for tests and
experiments.

The module exposes :func:`main` which acts as the entry point for
``python -m better5e``.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Sequence
from uuid import UUID

from .dao import FileDAO, GameObjectDAO, SQLiteDAO
from .factory import create_game_object
from .wizard import GameObjectWizard, WizardError, validate_dice

# ---------------------------------------------------------------------------
# DAO factory


def make_dao(args: argparse.Namespace) -> GameObjectDAO:
    """Return a DAO instance based on ``args``."""

    if args.store == "sqlite":
        return SQLiteDAO(Path(args.db))
    base = Path(args.data_dir)
    return FileDAO(base)


# ---------------------------------------------------------------------------
# Prompt helpers


def _render_prompt(field: dict, default: Any | None = None) -> str:
    label = field.get("label", field["key"])
    pieces = [label]
    if choices := field.get("choices"):
        pieces.append(f"({', '.join(str(c) for c in choices)})")
    if default not in (None, []):
        pieces.append(f"[default: {default}]")
    pieces.append(": ")
    return " ".join(pieces)


def _coerce_number(value: str) -> int | float:
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError("invalid number") from exc


def prompt_field(field: dict, *, default: Any | None = None, input_fn=input) -> Any:
    """Prompt the user for ``field`` and return the parsed value."""

    while True:  # loop until valid input is provided
        raw = input_fn(_render_prompt(field, default)).strip()
        if raw == "":
            if default is not None:
                return default
            if not field.get("required"):
                return [] if field.get("type") == "multiselect" else None
        ftype = field.get("type")
        try:
            if ftype == "text":
                return raw
            if ftype == "number":
                return _coerce_number(raw)
            if ftype in {"bool", "boolean"}:
                if raw.lower() in {"y", "yes", "true", "1"}:
                    return True
                if raw.lower() in {"n", "no", "false", "0"}:
                    return False
                raise ValueError("enter y/n")
            if ftype == "select":
                if raw in [str(c) for c in field.get("choices", [])]:
                    return raw
                raise ValueError("invalid choice")
            if ftype == "multiselect":
                if not raw:
                    return []
                values = [v.strip() for v in raw.split(",") if v.strip()]
                choices = field.get("choices", [])
                invalid = [v for v in values if v not in choices]
                if invalid:
                    raise ValueError(f"invalid choice: {invalid[0]}")
                return values
            if ftype == "dice":
                validate_dice(raw)
                return raw
            if ftype == "uuid_list":
                if not raw:
                    return []
                return [str(UUID(v.strip())) for v in raw.split(",") if v.strip()]
        except Exception as exc:
            print(exc)
    # pragma: no cover - loop always returns


# ---------------------------------------------------------------------------
# Command implementations


def _step_defaults(step: str, template: dict | None) -> dict:
    if not template:
        return {}
    if step == "core":
        return template.get("core", {})
    if step == "type_specific":
        return template.get("data", {})
    if step == "modifiers":
        return {"modifiers": template.get("modifiers", [])}
    if step == "grants":
        return {"grants": template.get("grants", [])}
    return {}


def _prompt_interactive(wiz: GameObjectWizard, obj_type: str, template: dict | None, *, input_fn=input) -> dict:
    sid = wiz.start(obj_type, template=template)
    spec = wiz.get_form_spec(obj_type)
    revision = 0
    for step in spec["steps"]:
        name = step["name"]
        if name == "review":
            break
        data: dict[str, Any] = {}
        defaults = _step_defaults(name, template)
        for field in step["fields"]:
            if name in {"modifiers", "grants"}:
                # simplified handling for collection steps
                if name == "modifiers":
                    data["modifiers"] = defaults.get("modifiers", [])
                else:
                    data["grants"] = defaults.get("grants", [])
                continue
            default = defaults.get(field["key"])
            val = prompt_field(field, default=default, input_fn=input_fn)
            if val is not None and val != []:
                data[field["key"]] = val
        wiz.apply(sid, data, revision=revision)
        revision += 1
        preview = wiz.preview(sid)
        print(json.dumps(preview, indent=2, sort_keys=True))
    result = wiz.finalize(sid, save=True)
    summary = {"uuid": result["uuid"], "type": result["type"], "name": result["model"]["name"]}
    print(json.dumps(summary, indent=2, sort_keys=True))
    return result


def cmd_new(args: argparse.Namespace, wiz: GameObjectWizard, *, input_fn=input) -> int:
    template = None
    if args.infile:
        template = json.loads(Path(args.infile).read_text())
    if args.non_interactive:
        sid = wiz.start(args.type, template=template)
        result = wiz.finalize(sid, save=True)
        summary = {"uuid": result["uuid"], "type": result["type"], "name": result["model"]["name"]}
        print(json.dumps(summary, indent=2, sort_keys=True))
        if args.verbose:
            print(json.dumps(result["model"], indent=2, sort_keys=True))
        return 0
    result = _prompt_interactive(wiz, args.type, template, input_fn=input_fn)
    if args.verbose:
        print(json.dumps(result["model"], indent=2, sort_keys=True, default=str))
    return 0


def cmd_edit(args: argparse.Namespace, wiz: GameObjectWizard, dao: GameObjectDAO, *, input_fn=input) -> int:
    obj = dao.load(UUID(args.uuid))
    template = {
        "core": {"name": obj.name},
        "data": obj.data,
        "modifiers": [m.model_dump() for m in obj.modifiers],
        "grants": [str(g) for g in obj.grants],
    }
    sid = wiz.load_existing(obj.uuid)
    spec = wiz.get_form_spec(obj.type)
    revision = 0
    for step in spec["steps"]:
        name = step["name"]
        if name == "review":
            break
        data: dict[str, Any] = {}
        defaults = _step_defaults(name, template)
        if name in {"modifiers", "grants"}:
            wiz.apply(sid, defaults, revision=revision)
            revision += 1
            continue
        for field in step["fields"]:
            default = defaults.get(field["key"])
            val = prompt_field(field, default=default, input_fn=input_fn)
            if val is not None and val != []:
                data[field["key"]] = val
        wiz.apply(sid, data, revision=revision)
        revision += 1
        preview = wiz.preview(sid)
        print(json.dumps(preview, indent=2, sort_keys=True))
    result = wiz.finalize(sid, save=True)
    summary = {"uuid": result["uuid"], "type": result["type"], "name": result["model"]["name"]}
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def cmd_show(args: argparse.Namespace, dao: GameObjectDAO) -> int:
    obj = dao.load(UUID(args.uuid))
    print(json.dumps(obj.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0


def cmd_preview(args: argparse.Namespace, dao: GameObjectDAO) -> int:
    obj = dao.load(UUID(args.uuid))
    payload = {
        "uuid": str(obj.uuid),
        "type": obj.type,
        "name": obj.name,
        "modifier_count": len(obj.modifiers),
        "grants": [str(g) for g in obj.grants],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_list(args: argparse.Namespace, dao: GameObjectDAO) -> int:
    rows: list[tuple[str, str, str]] = []
    if isinstance(dao, FileDAO):
        base = dao.base_path
        for type_dir in sorted(base.glob("*")):
            if not type_dir.is_dir():
                continue
            if args.type and type_dir.name != args.type:
                continue
            for f in sorted(type_dir.glob("*.json")):
                data = json.loads(f.read_text())
                rows.append((data["uuid"], data["type"], data.get("name")))
    else:  # SQLiteDAO
        cur = dao.conn.cursor()
        if args.type:
            cur.execute("SELECT uuid, type, data FROM game_objects WHERE type=?", (args.type,))
        else:
            cur.execute("SELECT uuid, type, data FROM game_objects")
        for uid, typ, data_s in cur.fetchall():
            data = json.loads(data_s)
            rows.append((uid, typ, data.get("name")))
    for uid, typ, name in rows:
        print(f"{uid} {typ} {name}")
    return 0


def cmd_delete(args: argparse.Namespace, dao: GameObjectDAO, *, input_fn=input) -> int:
    obj = dao.load(UUID(args.uuid))
    if not args.yes:
        resp = input_fn("Are you sure? (y/N): ").strip().lower()
        if resp not in {"y", "yes"}:
            print("aborted")
            return 1
    if isinstance(dao, FileDAO):
        path = dao._path(obj)  # type: ignore[attr-defined]
        if path.exists():
            path.unlink()
    else:
        dao.conn.execute("DELETE FROM game_objects WHERE uuid=?", (args.uuid,))
        dao.conn.commit()
    return 0


def cmd_export(args: argparse.Namespace, dao: GameObjectDAO) -> int:
    obj = dao.load(UUID(args.uuid))
    Path(args.out).write_text(json.dumps(obj.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0


def cmd_import(args: argparse.Namespace, dao: GameObjectDAO) -> int:
    data = json.loads(Path(args.infile).read_text())
    if args.type:
        data["type"] = args.type
    obj = create_game_object(data)
    dao.save(obj)
    return 0


# ---------------------------------------------------------------------------
# Argument parsing and main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="better5e")
    parser.add_argument("--store", choices=["file", "sqlite"], default="file")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--db", default="data/better5e.sqlite")
    parser.add_argument("--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new")
    p_new.add_argument("type", choices=["feature", "item", "spell", "race", "background", "class"])
    p_new.add_argument("--non-interactive", action="store_true")
    p_new.add_argument("--in", dest="infile")

    p_edit = sub.add_parser("edit")
    p_edit.add_argument("uuid")

    p_preview = sub.add_parser("preview")
    p_preview.add_argument("uuid")

    p_list = sub.add_parser("list")
    p_list.add_argument("type", nargs="?")

    p_show = sub.add_parser("show")
    p_show.add_argument("uuid")

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("uuid")
    p_delete.add_argument("--yes", action="store_true")

    p_export = sub.add_parser("export")
    p_export.add_argument("uuid")
    p_export.add_argument("--out", required=True)

    p_import = sub.add_parser("import")
    p_import.add_argument("--type", required=True)
    p_import.add_argument("--in", dest="infile", required=True)

    return parser


def main(argv: Sequence[str] | None = None, *, input_fn=input) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dao = make_dao(args)
    wiz = GameObjectWizard(dao)
    try:
        if args.command == "new":
            return cmd_new(args, wiz, input_fn=input_fn)
        if args.command == "edit":
            return cmd_edit(args, wiz, dao, input_fn=input_fn)
        if args.command == "preview":
            return cmd_preview(args, dao)
        if args.command == "list":
            return cmd_list(args, dao)
        if args.command == "show":
            return cmd_show(args, dao)
        if args.command == "delete":
            return cmd_delete(args, dao, input_fn=input_fn)
        if args.command == "export":
            return cmd_export(args, dao)
        if args.command == "import":
            return cmd_import(args, dao)
    except WizardError as exc:
        detail = exc.detail if exc.detail is not None else "-"
        field = exc.field if exc.field is not None else "-"
        print(f"error: {exc.code}\nfield: {field}\nmessage: {exc.message}\ndetail: {detail}")
        return 1
    except Exception as exc:  # pragma: no cover - defensive
        print(f"error: {exc}")
        return 1
    return 0


__all__ = ["main", "make_dao"]
