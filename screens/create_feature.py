# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore
from models.feature import Feature  # Assuming Feature is defined in models.feature

class CreateFeature(QtWidgets.QWidget):
    def __init__(self, app: QtWidgets.QApplication):
        """Initialize the Create Feature screen of the application."""
        super().__init__()
        self.app = app
        self.title = "Create Feature"
        # Assuming Feature is defined elsewhere
        self.container = QtWidgets.QVBoxLayout(self)

        # Title
        self.container.addWidget(QtWidgets.QLabel("Create a New Feature"))

        # Feature Name Input
        self.feature_name_input = QtWidgets.QLineEdit()
        self.feature_name_input.setPlaceholderText("Feature Name")
        self.container.addWidget(self.feature_name_input)

        # Description Input
        self.description_input = QtWidgets.QTextEdit()
        self.description_input.setPlaceholderText("Feature Description")
        self.container.addWidget(self.description_input)

        # Check Box for Feature Type (This Feature Modifies a Save, This Feature Modifies a Skill, This Feature Modifies a Stat, etc.)
        FeatureTypeGroup = QtWidgets.QGroupBox("Feature Type")
        self.feature_type_layout = QtWidgets.QVBoxLayout()
        for feature_type in [
            "Weapon Attack Modifier",
            "Weapon Damage Modifier",
            "Spell Attack Modifier",
            "Spell Damage Modifier",
            "Spell Save DC Modifier",
            "Skill Modifier",
            "Save Modifier",
            "Stat Modifier"
        ]:
            checkbox = QtWidgets.QCheckBox(feature_type)
            self.feature_type_layout.addWidget(checkbox)

        FeatureTypeGroup.setLayout(self.feature_type_layout)
        self.container.addWidget(FeatureTypeGroup)
        # Add a separator line
        self.container.addWidget(QtWidgets.QFrame(frameShape=QtWidgets.QFrame.HLine, frameShadow=QtWidgets.QFrame.Sunken))
        # Add a spacer to separate the feature type checkboxes from the save button
        self.container.addStretch(1)
        # Add a spacer to separate the feature type checkboxes from the save button
        self.container.addWidget(QtWidgets.QLabel("Click 'Save Feature' to save your changes."))
        self.container.addStretch(1)
        # Save Button
        self.save_button = QtWidgets.QPushButton("Save Feature")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.save_button.clicked.connect(self.save_feature)
        self.cancel_button.clicked.connect(self.app.pop_widget)
        self.cancel_button.setToolTip("Return to the previous screen without saving.")
        self.save_button.setToolTip("Save the feature and return to the previous screen.")
        self.button_container = QtWidgets.QHBoxLayout()
        self.button_container.addWidget(self.save_button)
        self.button_container.addWidget(self.cancel_button)
        self.container.addLayout(self.button_container)

    @QtCore.Slot()
    def save_feature(self):
        """Handle saving the feature."""
        feature_name = self.feature_name_input.text()
        description = self.description_input.toPlainText()
        
        if feature_name and description:
            print(f"Feature '{feature_name}' saved with description: {description}")
            # Here you would typically save the feature to a database or file.
            self.feature_name_input.clear()
            self.description_input.clear()
        else:
            print("Please fill in both fields.")