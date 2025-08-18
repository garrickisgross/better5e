from __future__ import annotations

import random
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
    QAbstractItemView,
)

from better5e.UI.core.style.theme import add_shadow


def _fmt_time(ts: datetime) -> str:
    import sys

    same_day = ts.date() == datetime.now(ts.tzinfo).date()
    if same_day:
        fmt = "%#I:%M %p" if sys.platform == "win32" else "%-I:%M %p"
        return ts.strftime(fmt).lstrip("0")
    if ts.year == datetime.now(ts.tzinfo).year:
        return ts.strftime("%b %d · %I:%M %p").lstrip("0")
    return ts.strftime("%b %d, %Y")


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
        chips.setSpacing(6)
        roll_labels: list[QLabel] = []
        for r in rolls:
            lab = QLabel(str(r))
            lab.setProperty("class", "chip")
            chips.addWidget(lab)
            roll_labels.append(lab)
        chips.addStretch(1)
        time_lbl = QLabel(_fmt_time(ts))
        time_lbl.setObjectName("RollMeta")
        chips.addWidget(time_lbl)
        layout.addLayout(chips)

        self.notation_label = notation_lbl
        self.total_label = total_lbl
        self.meta_label = time_lbl
        self.roll_labels = roll_labels


class RollHistoryPanel(QListWidget):
    """A bottom-anchored feed of roll cards."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSpacing(10)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._reroll_item)

        self._stick_bottom: bool = True
        sb = self.verticalScrollBar()
        sb.valueChanged.connect(self._on_scroll_value_changed)
        sb.rangeChanged.connect(self._maybe_snap_to_bottom)
        self.itemSelectionChanged.connect(
            lambda: setattr(self, "_stick_bottom", self._is_at_bottom() and not self.selectedItems())
        )

    def _parse_notation(self, notation: str) -> tuple[dict[int, int], int]:
        dice: dict[int, int] = {}
        mod = 0
        parts = notation.replace("-", "+-").split("+")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if "d" in part:
                count_str, sides_str = part.split("d", 1)
                dice[int(sides_str)] = dice.get(int(sides_str), 0) + int(count_str)
            else:
                mod += int(part)
        return dice, mod

    # ---------- public API ----------
    def add_roll_card(self, card_widget: QWidget, data: dict | None = None) -> None:
        """Append a roll card at the bottom."""
        item = QListWidgetItem()
        item.setSizeHint(card_widget.sizeHint())
        if data is not None:
            item.setData(Qt.ItemDataRole.UserRole, data)
        self.addItem(item)
        self.setItemWidget(item, card_widget)
        # rangeChanged will fire -> _maybe_snap_to_bottom handles scroll

    def add_entry(self, text: str) -> None:
        """Parse a result string and append it to the list."""
        text = text.strip()
        if " = " not in text or "(" not in text or not text.endswith(")"):
            return
        notation_part, rest = text.split(" = ", 1)
        total_part, rolls_part = rest.split(" (", 1)
        try:
            total_i = int(total_part)
        except ValueError:
            return
        rolls = [int(r.strip()) for r in rolls_part[:-1].split(",")]
        dice_map, mod = self._parse_notation(notation_part)
        ts = datetime.now()

        card = RollCard(notation_part, total_i, rolls, ts)
        if dice_map.get(20) == 1 and len(rolls) == sum(dice_map.values()) and rolls[0] == 20:
            card.setProperty("crit", True)

        add_shadow(card, blur=18, y=3)

        data = {
            "notation": notation_part,
            "total": total_i,
            "rolls": rolls,
            "mod": mod,
            "dice": dice_map,
        }
        self.add_roll_card(card, data)

    def clearHistory(self) -> None:
        """Remove all roll entries and reset scroll anchoring."""
        self.clear()
        self._stick_bottom = True
        # After first paint, stick to bottom
        self._maybe_snap_to_bottom(0, self.verticalScrollBar().maximum())

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
            self.clearHistory()

    def _copy_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        text = f"{data['notation']} = {data['total']} ({', '.join(map(str, data['rolls']))})"
        QApplication.clipboard().setText(text, QClipboard.Mode.Clipboard)

    # reroll ---------------------------------------------------------------
    def _reroll_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        dice: dict[int, int] = data["dice"]
        mod = data["mod"]
        rolls: list[int] = []
        for sides, count in dice.items():
            rolls.extend(random.randint(1, sides) for _ in range(count))
        total = sum(rolls) + mod
        text = f"{data['notation']} = {total} ({', '.join(map(str, rolls))})"
        self.add_entry(text)

    # ---------- autoscroll internals ----------
    def _is_at_bottom(self) -> bool:
        sb = self.verticalScrollBar()
        return sb.value() >= sb.maximum() - 2

    def _on_scroll_value_changed(self, _value: int) -> None:
        self._stick_bottom = self._is_at_bottom()

    def _maybe_snap_to_bottom(self, _minv: int, maxv: int) -> None:
        if self._stick_bottom:
            self.verticalScrollBar().setValue(maxv)

    def showEvent(self, e) -> None:  # pragma: no cover - Qt event
        super().showEvent(e)
        self._maybe_snap_to_bottom(0, self.verticalScrollBar().maximum())
