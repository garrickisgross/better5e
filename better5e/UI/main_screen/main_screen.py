import random
from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QFrame,
    QPushButton,
    QSizePolicy,
)
from typing import TYPE_CHECKING

from better5e.UI.core.basepage import BasePage
from better5e.UI.main_screen.components.roll_history import RollHistoryPanel, RollCard
from better5e.UI.main_screen.components.dice_options import DiceOptionsPanel
from better5e.UI.main_screen.components.section_header import Section
from better5e.UI.main_screen.components.card_grid import CardGrid
from better5e.UI.main_screen.components.homebrew_panel import HomebrewPanel
from better5e.UI.style.theme import add_shadow
from better5e.UI.style.tokens import gutter

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from better5e.UI.core.app import App


class MainScreen(BasePage):
    """Home page container widget."""

    seeAllCharacters = pyqtSignal()
    createNewCharacter = pyqtSignal()
    seeAllCampaigns = pyqtSignal()
    createNewCampaign = pyqtSignal()
    openHomebrew = pyqtSignal(str)

    def __init__(self, app: "App") -> None:
        super().__init__(app, "Home")

        body = self.layout()
        body.setContentsMargins(0, 0, 0, 0)

        # Root 3-column layout -------------------------------------------------
        G = gutter() if callable(gutter) else 20
        root = QHBoxLayout()
        root.setContentsMargins(G, 8, G, 12)
        root.setSpacing(12)
        body.addLayout(root)

        # Left sidebar --------------------------------------------------------
        leftPane = QWidget()
        leftPane.setObjectName("LeftPane")
        leftCol = QVBoxLayout(leftPane)
        self.roll_history = RollHistoryPanel()
        leftCol.addWidget(self.roll_history)
        self.dice_panel = DiceOptionsPanel()
        self.dice_panel.rollRequested.connect(self._on_roll_requested)
        leftCol.addWidget(self.dice_panel)
        leftCol.setStretch(0, 1)

        leftPane.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        leftPane.setMaximumWidth(400)

        # Center content ------------------------------------------------------
        self.centerScroll = QScrollArea()
        self.centerScroll.setObjectName("CenterScroll")
        self.centerScroll.setFrameShape(QFrame.Shape.NoFrame)
        self.centerScroll.setWidgetResizable(True)

        centerWidget = QWidget()
        centerWidget.setObjectName("CenterPane")
        self.centerScroll.setWidget(centerWidget)
        centerCol = QVBoxLayout(centerWidget)
        centerCol.setContentsMargins(8, 0, 8, 0)
        centerCol.setSpacing(12)

        # Characters section
        charactersSection = Section("My Characters")
        self.characters_header = charactersSection.header
        self.characters_header.seeAll.connect(self.seeAllCharacters.emit)
        charactersSection.body.addWidget(
            CardGrid(["Character 1", "Character 2", "Character 3"])
        )
        self.characters_create = QPushButton("Create New")
        self.characters_create.setProperty("class", "primary")
        self.characters_create.clicked.connect(self.createNewCharacter.emit)
        charactersSection.body.addWidget(self.characters_create)

        # Campaigns section
        campaignsSection = Section("My Campaigns")
        self.campaigns_header = campaignsSection.header
        self.campaigns_header.seeAll.connect(self.seeAllCampaigns.emit)
        campaignsSection.body.addWidget(
            CardGrid(["Campaign 1", "Campaign 2", "Campaign 3"])
        )
        self.campaigns_create = QPushButton("Create New")
        self.campaigns_create.setProperty("class", "primary")
        self.campaigns_create.clicked.connect(self.createNewCampaign.emit)
        campaignsSection.body.addWidget(self.campaigns_create)

        centerCol.addWidget(charactersSection)
        centerCol.addWidget(campaignsSection)
        centerCol.addStretch(1)

        # Right sidebar -------------------------------------------------------
        rightPane = HomebrewPanel(app)
        rightPane.setObjectName("RightPane")
        rightPane.openHomebrew.connect(self.openHomebrew.emit)
        rightPane.setMinimumWidth(260)
        rightPane.setMaximumWidth(320)
        rightPane.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Assemble layout -----------------------------------------------------
        root.addWidget(leftPane)
        root.addWidget(self.centerScroll)
        root.addWidget(rightPane)

        # Keep sidebars compact while center expands
        root.setStretch(0, 0)
        root.setStretch(1, 1)
        root.setStretch(2, 0)

        self.homebrew_panel = rightPane

    # roll handling -----------------------------------------------------
    def _on_roll_requested(self, dice: dict[int, int], modifier: int) -> None:
        rolls: list[int] = []
        notation_parts: list[str] = []
        total = modifier
        for sides, count in dice.items():
            part_rolls = [random.randint(1, sides) for _ in range(count)]
            rolls.extend(part_rolls)
            total += sum(part_rolls)
            notation_parts.append(f"{count}d{sides}")
        notation = " + ".join(notation_parts)
        if modifier:
            sign = "+" if modifier > 0 else "-"
            notation = f"{notation} {sign} {abs(modifier)}" if notation else f"{modifier}"
        ts = datetime.now()
        card = RollCard(notation.strip(), total, rolls, ts)
        if dice.get(20) == 1 and len(rolls) == sum(dice.values()) and rolls and rolls[0] == 20:
            card.setProperty("crit", True)
        add_shadow(card, blur=18, y=3)
        data = {
            "notation": notation.strip(),
            "total": total,
            "rolls": rolls,
            "mod": modifier,
            "dice": dice,
        }
        self.roll_history.add_roll_card(card, data)
