from PySide6 import QtCore



class MainScreenRightPanelController:

    @QtCore.Slot()
    def create_class(self):
        print("Create Class button clicked")
        # Logic to create a class
        # For example, open a dialog to input class details

    @QtCore.Slot()
    def create_feature(self):
        print("Create Feature button clicked")
        # Logic to create a feature
        # For example, open a dialog to input feature details

    @QtCore.Slot()
    def create_item(self):
        print("Create Item button clicked")
        # Logic to create an item
        # For example, open a dialog to input item details

    @QtCore.Slot()
    def create_weapon(self):
        print("Create Weapon button clicked")
        # Logic to create a weapon
        # For example, open a dialog to input weapon details

    @QtCore.Slot()
    def create_spell(self):
        print("Create Spell button clicked")
        # Logic to create a spell
        # For example, open a dialog to input spell details