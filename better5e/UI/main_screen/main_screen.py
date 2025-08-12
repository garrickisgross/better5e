from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QPushButton,
)
from typing import TYPE_CHECKING

from better5e.UI.core.basepage import BasePage
from better5e.UI.main_screen.components.roll_history import RollHistoryPanel
from better5e.UI.main_screen.components.dice_options import DiceOptionsPanel
from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.main_screen.components.card_grid import CardGrid
from better5e.UI.main_screen.components.homebrew_panel import HomebrewPanel

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from better5e.UI.core.app import App


class MainScreen(BasePage):
    """Home page container widget."""

    seeAllCharacters = pyqtSignal()
    createNewCharacter = pyqtSignal()
    seeAllCampaigns = pyqtSignal()
    createNewCampaign = pyqtSignal()
    openHomebrew = pyqtSignal(str)

    def __init__(self, app: "App"):
        super().__init__(app, "Home")
        body = self.layout()

        columns = QHBoxLayout()
        body.addLayout(columns)

        # Left sidebar
        left = QVBoxLayout()
        self.roll_history = RollHistoryPanel()
        left.addWidget(self.roll_history)
        self.dice_panel = DiceOptionsPanel()
        self.dice_panel.rollMade.connect(self.roll_history.add_entry)
        left.addWidget(self.dice_panel)
        left.setStretch(0, 1)
        columns.addLayout(left)

        # Center content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        columns.addWidget(scroll, 1)

        center_widget = QWidget()
        scroll.setWidget(center_widget)
        center_layout = QVBoxLayout(center_widget)

        # Characters section
        self.characters_header = SectionHeader("My Characters")
        self.characters_header.seeAll.connect(self.seeAllCharacters.emit)
        center_layout.addWidget(self.characters_header)
        center_layout.addWidget(CardGrid(["Character 1", "Character 2", "Character 3"]))
        self.characters_create = QPushButton("Create New")
        self.characters_create.setProperty("class", "primary")
        self.characters_create.clicked.connect(self.createNewCharacter.emit)
        center_layout.addWidget(self.characters_create)

        # Campaigns section
        self.campaigns_header = SectionHeader("My Campaigns")
        self.campaigns_header.seeAll.connect(self.seeAllCampaigns.emit)
        center_layout.addWidget(self.campaigns_header)
        center_layout.addWidget(CardGrid(["Campaign 1", "Campaign 2", "Campaign 3"]))
        self.campaigns_create = QPushButton("Create New")
        self.campaigns_create.setProperty("class", "primary")
        self.campaigns_create.clicked.connect(self.createNewCampaign.emit)
        center_layout.addWidget(self.campaigns_create)

        center_layout.addStretch()

        # Right sidebar
        self.homebrew_panel = HomebrewPanel()
        self.homebrew_panel.openHomebrew.connect(self.openHomebrew.emit)
        columns.addWidget(self.homebrew_panel)
