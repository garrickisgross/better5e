import json
from pathlib import Path

import sqlite3
import pytest

from better5e.cli import main


def run_cli(argv, inputs):
    it = iter(inputs)
    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise AssertionError("not enough input for prompts")
    return main(argv, input_fn=fake_input)


def create_item_json(tmp_path: Path) -> Path:
    data = {
        "core": {"name": "Sword"},
        "data": {"category": "weapon", "damage": "1d8", "damage_type": "slashing"},
        "modifiers": [],
        "grants": [],
    }
    path = tmp_path / "tmpl.json"
    path.write_text(json.dumps(data))
    return path


def test_new_item_interactive_happy_path(tmp_path):
    data_dir = tmp_path / "data"
    inputs = [
        "Sword",  # name
        "weapon",  # category
        "2",  # weight (number parsing)
        "",  # value
        "light,versatile",  # properties (multiselect)
        "1d8",  # damage
        "slashing",  # damage type
        "",  # ac base
        "",  # stealth disadvantage
    ]
    rc = run_cli(["--data-dir", str(data_dir), "--verbose", "new", "item"], inputs)
    assert rc == 0
    files = list((data_dir / "item").glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["name"] == "Sword"
    assert data["data"]["damage"] == "1d8"


def test_new_spell_from_json_non_interactive(tmp_path):
    tmpl = {
        "core": {"name": "Zap"},
        "data": {"level": 1, "school": "evocation", "damage": "1d6", "damage_type": "fire"},
        "modifiers": [],
        "grants": [],
    }
    inpath = tmp_path / "spell.json"
    inpath.write_text(json.dumps(tmpl))
    db = tmp_path / "store.sqlite"
    rc = run_cli(["--store", "sqlite", "--db", str(db), "new", "spell", "--non-interactive", "--in", str(inpath)], [])
    assert rc == 0
    # verify persisted
    conn = sqlite3.connect(db)
    cur = conn.execute("SELECT data FROM game_objects")
    row = cur.fetchone()
    assert row and json.loads(row[0])["name"] == "Zap"


def test_edit_existing_roundtrip(tmp_path):
    data_dir = tmp_path / "data"
    tmpl = create_item_json(tmp_path)
    rc = run_cli(["--data-dir", str(data_dir), "new", "item", "--non-interactive", "--in", str(tmpl)], [])
    assert rc == 0
    item_file = next((data_dir / "item").glob("*.json"))
    uid = item_file.stem
    inputs = [
        "Great Sword",  # new name
        "", "", "", "", "", "", "", "",  # keep defaults
    ]
    rc = run_cli(["--data-dir", str(data_dir), "edit", uid], inputs)
    assert rc == 0
    data = json.loads(item_file.read_text())
    assert data["name"] == "Great Sword"


def test_list_show_delete_export_import(tmp_path):
    data_dir = tmp_path / "data"
    tmpl = create_item_json(tmp_path)
    run_cli(["--data-dir", str(data_dir), "new", "item", "--non-interactive", "--in", str(tmpl)], [])
    item_file = next((data_dir / "item").glob("*.json"))
    uid = item_file.stem

    # list
    rc = run_cli(["--data-dir", str(data_dir), "list"], [])
    assert rc == 0

    # show
    rc = run_cli(["--data-dir", str(data_dir), "show", uid], [])
    assert rc == 0

    # preview
    rc = run_cli(["--data-dir", str(data_dir), "preview", uid], [])
    assert rc == 0

    # export
    out = tmp_path / "export.json"
    rc = run_cli(["--data-dir", str(data_dir), "export", uid, "--out", str(out)], [])
    assert rc == 0 and out.exists()

    # delete with confirmation
    rc = run_cli(["--data-dir", str(data_dir), "delete", uid], ["y"])
    assert rc == 0
    assert not item_file.exists()

    # import
    rc = run_cli(["--data-dir", str(data_dir), "import", "--type", "item", "--in", str(out)], [])
    assert rc == 0
    assert any((data_dir / "item").glob("*.json"))


def test_invalid_choice_and_reprompt(tmp_path, capsys):
    data_dir = tmp_path / "data"
    inputs = [
        "Sword",  # name
        "bad", "weapon",  # category with retry
        "2",  # weight
        "",  # value
        "light",  # properties
        "1d8",
        "slashing",
        "",
        "",  # stealth disadvantage default
    ]
    rc = run_cli(["--data-dir", str(data_dir), "new", "item"], inputs)
    captured = capsys.readouterr().out
    assert "invalid choice" in captured
    assert rc == 0
    assert any((data_dir / "item").glob("*.json"))
