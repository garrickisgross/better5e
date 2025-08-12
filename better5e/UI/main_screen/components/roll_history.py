from __future__ import annotations

import random
import re
from datetime import datetime

from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMenu,
)


def _fmt_time(ts: datetime) -> str:
    """Return a context-aware timestamp string."""
    now = datetime.now()
    if ts.date() == now.date():
        return ts.strftime("%I:%M %p").lstrip("0")
    if ts.year == now.year:
        return f"{ts.strftime('%b')} {ts.day} · {ts.strftime('%I:%M %p').lstrip('0')}"
    return ts.strftime("%b %d, %Y")

from better5e.UI.style.theme import add_shadow


class RollCard(QWidget):
    """Widget representing a single dice roll."""

    def __init__(self, notation: str, total: int, rolls: list[int], ts: datetime) -> None:
        super().__init__()
        self.setObjectName("RollCard")
        self.timestamp = ts

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        notation_lbl = QLabel(notation)
        notation_lbl.setObjectName("RollNotation")
        total_lbl = QLabel(str(total))
        total_lbl.setObjectName("RollTotal")

        row.addWidget(notation_lbl)
        row.addStretch(1)
        row.addWidget(total_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(row)

        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(6)
        chip_labels: list[QLabel] = []
        for r in rolls:
            lab = QLabel(str(r))
            lab.setProperty("class", "chip")
            chips.addWidget(lab)
            chip_labels.append(lab)
        chips.addStretch(1)
        time_lbl = QLabel(_fmt_time(ts))
        time_lbl.setObjectName("RollMeta")
        chips.addWidget(time_lbl)
        layout.addLayout(chips)

        self.notation_label = notation_lbl
        self.total_label = total_lbl
        self.meta_label = time_lbl
        self.chip_labels = chip_labels


class RollHistoryPanel(QListWidget):
    """List widget showing past dice rolls."""

    _ROLL_RE = re.compile(r"(\d+)d(\d+)([+-]\d+) = (\d+) \(([^)]+)\)")

    def __init__(self) -> None:
        super().__init__()
        self.setSpacing(8)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._reroll_item)

    def add_entry(self, text: str) -> None:
        """Append a roll result to the list."""
        match = self._ROLL_RE.fullmatch(text.strip())
        if not match:
            return

        count, sides, mod, total, rolls_str = match.groups()
        count_i, sides_i, mod_i = int(count), int(sides), int(mod)
        total_i = int(total)
        rolls = [int(r.strip()) for r in rolls_str.split(',')]
        notation = f"{count_i}d{sides_i}{mod_i:+d}"
        ts = datetime.now()

        card = RollCard(notation, total_i, rolls, ts)
        if count_i == 1 and sides_i == 20 and rolls[0] == 20:
            card.setProperty("crit", True)

        add_shadow(card, blur=18, y=3)

        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 72))
        item.setData(Qt.ItemDataRole.UserRole, {
            "notation": notation,
            "total": total_i,
            "rolls": rolls,
            "mod": mod_i,
            "sides": sides_i,
            "count": count_i,
        })
        self.addItem(item)
        self.setItemWidget(item, card)

    def clear_history(self) -> None:
        """Remove all roll entries."""
        self.clear()

    # context menu ---------------------------------------------------------
    def _show_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        clear_action = menu.addAction("Clear All")
        action = menu.exec(self.viewport().mapToGlobal(pos))
        if action == copy_action and item:
            self._copy_item(item)
        elif action == delete_action and item:
            row = self.row(item)
            self.takeItem(row)
        elif action == clear_action:
            self.clear_history()

    def _copy_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        text = f"{data['notation']} = {data['total']} ({', '.join(map(str, data['rolls']))})"
        QApplication.clipboard().setText(text, QClipboard.Mode.Clipboard)

    # reroll ---------------------------------------------------------------
    def _reroll_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        count, sides, mod = data["count"], data["sides"], data["mod"]
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + mod
        text = f"{count}d{sides}{mod:+d} = {total} ({', '.join(map(str, rolls))})"
        self.add_entry(text)
