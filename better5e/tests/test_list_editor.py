from PyQt6.QtWidgets import QApplication

from better5e.UI.components.list_editor import ListEditor

app = QApplication([])


def test_reorder_persists():
    editor = ListEditor(int, [1, 2, 3])
    editor.move(0, 2)
    assert editor.items == [2, 3, 1]
