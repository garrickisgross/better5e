"""
UI page for creating a new Feature.

This page is displayed when the user selects “Create Feature” from the
Homebrew panel. It presents a tabbed form for entering the basic
properties of a Feature (name, description, uses, recharge) and stub
tabs for actions, modifiers and grants. Upon submission, the form
validates required fields, constructs a Feature model instance and
saves it via the DAO. A back button allows the user to cancel and
return to the previous screen.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QTabWidget,
    QMessageBox,
)

from better5e.UI.core.basepage import BasePage
from better5e.UI.core.style.tokens import gutter
from better5e.UI.components.actions_editor import ActionsEditor
from better5e.UI.components.modifiers_editor import ModifiersEditor
from better5e.UI.components.grants_editor import GrantsEditor
from better5e.models.game_object import Feature
from better5e.models.enums import RechargeType
from better5e.dao.sqlite import DAO


class FeatureFormPage(BasePage):
    """A form for creating a new Feature."""

    def __init__(self, app) -> None:
        # Use the object name "Feature" so the app title shows “better5e – Feature”.
        super().__init__(app, "Feature")

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        """Assemble widgets for the page."""
        layout: QVBoxLayout = self.layout()  # type: ignore[assignment]
        layout.setContentsMargins(gutter(), gutter(), gutter(), gutter())
        layout.setSpacing(12)

        # Header row with back button and page title
        header = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.app.pop)
        header.addWidget(back_btn)
        title_label = QLabel("Create Feature")
        title_label.setObjectName("FeatureFormTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        header.addWidget(title_label)
        header.addStretch(1)
        layout.addLayout(header)

        # Tabs for organizing fields
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Info tab
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(gutter(), gutter(), gutter(), gutter())
        info_layout.setSpacing(12)

        # Name field
        name_label = QLabel("Name")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter feature name")
        info_layout.addWidget(name_label)
        info_layout.addWidget(self.name_input)

        # Description field (required)
        desc_label = QLabel("Description")
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter feature description (required)")
        self.desc_input.setAcceptRichText(False)
        self.desc_input.setFixedHeight(150)
        info_layout.addWidget(desc_label)
        info_layout.addWidget(self.desc_input)

        # Uses Max
        uses_layout = QHBoxLayout()
        uses_label = QLabel("Uses (max)")
        self.uses_input = QSpinBox()
        self.uses_input.setMinimum(0)
        self.uses_input.setMaximum(999)
        self.uses_input.setValue(0)
        uses_layout.addWidget(uses_label)
        uses_layout.addWidget(self.uses_input)
        info_layout.addLayout(uses_layout)

        # Recharge type
        recharge_layout = QHBoxLayout()
        recharge_label = QLabel("Recharge")
        self.recharge_input = QComboBox()
        # Populate combo with RechargeType names
        for rt in RechargeType:
            # Use title-case names for display (e.g. LONG_REST -> Long Rest)
            name = rt.name.replace("_", " ").title()
            self.recharge_input.addItem(name, rt)
        self.recharge_input.setEnabled(False)  # disabled when uses == 0
        recharge_layout.addWidget(recharge_label)
        recharge_layout.addWidget(self.recharge_input)
        info_layout.addLayout(recharge_layout)

        # Connect enabling/disabling recharge based on uses
        self.uses_input.valueChanged.connect(self._on_uses_changed)

        # Stretch to push controls to top
        info_layout.addStretch(1)

        tabs.addTab(info_widget, "Info")

        # Actions tab
        self.actions_editor = ActionsEditor()
        tabs.addTab(self.actions_editor, "Actions")

        # Modifiers tab
        self.modifiers_editor = ModifiersEditor()
        tabs.addTab(self.modifiers_editor, "Modifiers")

        # Grants tab
        self.grants_editor = GrantsEditor()
        tabs.addTab(self.grants_editor, "Grants")

        # Footer with submit button
        footer = QHBoxLayout()
        footer.addStretch(1)
        self.submit_button = QPushButton("Create")
        self.submit_button.setProperty("class", "primary")
        self.submit_button.clicked.connect(self._on_submit)
        self.submit_button.setEnabled(False)  # initial state until validation
        footer.addWidget(self.submit_button)
        layout.addLayout(footer)

        # Form validation: enable submit when required fields are valid
        self.name_input.textChanged.connect(self._update_submit_enabled)
        self.desc_input.textChanged.connect(self._update_submit_enabled)
        self.recharge_input.currentIndexChanged.connect(self._update_submit_enabled)
        self.uses_input.valueChanged.connect(self._update_submit_enabled)

    # ------------------------------------------------------------------
    # Validation and dynamic behaviour
    # ------------------------------------------------------------------
    def _on_uses_changed(self, value: int) -> None:
        """Enable recharge input when uses > 0; disable otherwise."""
        self.recharge_input.setEnabled(value > 0)
        # When uses go to zero, clear the recharge selection
        if value == 0:
            self.recharge_input.setCurrentIndex(-1)
        self._update_submit_enabled()

    def _update_submit_enabled(self) -> None:
        """Update the enabled state of the submit button based on validity."""
        name_ok = bool(self.name_input.text().strip())
        desc_ok = bool(self.desc_input.toPlainText().strip())
        # If uses > 0 then recharge must be selected; index >= 0
        uses = self.uses_input.value()
        recharge_ok = True
        if uses > 0:
            recharge_ok = self.recharge_input.currentIndex() >= 0
        self.submit_button.setEnabled(name_ok and desc_ok and recharge_ok)

    # ------------------------------------------------------------------
    # Submission handling
    # ------------------------------------------------------------------
    def _on_submit(self) -> None:
        """Validate input, create a Feature object, save it via DAO, and return."""
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Missing Description", "Feature description is required.")
            return
        # Determine uses_max and recharge
        uses_max: Optional[int] = None
        recharge: Optional[RechargeType] = None
        uses_val = self.uses_input.value()
        if uses_val > 0:
            uses_max = uses_val
            data = self.recharge_input.currentData()
            if isinstance(data, RechargeType):
                recharge = data

        actions = self.actions_editor.get_actions()
        modifiers = self.modifiers_editor.get_modifiers()
        grants = self.grants_editor.get_grants()

        # Construct the Feature model
        try:
            feature = Feature(
                name=name,
                desc=desc,
                uses_max=uses_max,
                recharge=recharge,
                actions=actions,
                modifiers=modifiers,
                grants=grants,
            )
        except Exception as exc:
            # Unexpected validation error; show message
            QMessageBox.critical(self, "Error", f"Failed to create feature: {exc}")
            return

        # Save the feature via the DAO
        try:
            dao = DAO()
            dao.save(feature)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to save feature: {exc}")
            return

        # Inform the user of success and pop back to previous page
        QMessageBox.information(self, "Feature Created", f"Feature '{feature.name}' was created successfully.")
        self.app.pop()
