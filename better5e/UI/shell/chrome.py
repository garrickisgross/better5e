from __future__ import annotations
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMainWindow,
    QFrame,
    QSizePolicy,
)
from better5e.UI.style.tokens import gutter


# Keep the title bar aligned with main screen gutters.  This value should
# mirror the horizontal margins used in ``main_screen.py`` so the title text
# lines up exactly with the app content (e.g. the dice box).
# Outer gutter matches the main screen margins.  The title text is indented
# slightly further to align with the dice panel content below.
GUTTER = gutter() if callable(gutter) else 20
TITLE_INDENT = 8


class TitleBar(QFrame):
    """Custom title bar with app title on left and window controls on right."""
    HEIGHT = 40

    def __init__(self, parent: QWidget | None = None, title: str = "better5e"):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(self.HEIGHT)
        self._mouse_pos: QPoint | None = None

        row = QHBoxLayout(self)
        row.setContentsMargins(GUTTER, 0, GUTTER, 0)
        row.setSpacing(8)

        self.title = QLabel(title, self)
        self.title.setObjectName("AppTitle")
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.title.setIndent(TITLE_INDENT)
        self.title.setContentsMargins(0, 2, 0, 0)
        f = self.title.font()
        f.setPixelSize(20)
        f.setWeight(700)
        self.title.setFont(f)

        self.btnMin = QPushButton("–", self);  self.btnMin.setObjectName("WinBtnMin")
        self.btnMax = QPushButton("□", self);  self.btnMax.setObjectName("WinBtnMax")
        self.btnClose = QPushButton("×", self); self.btnClose.setObjectName("WinBtnClose")

        for b, tip in [
            (self.btnMin, "Minimize"),
            (self.btnMax, "Maximize/Restore"),
            (self.btnClose, "Close"),
        ]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setProperty("class", "winbtn")
            b.setToolTip(tip)
            b.setFixedSize(42, 32)
            f = b.font()
            f.setPixelSize(16)
            f.setWeight(600)
            b.setFont(f)

        row.addWidget(self.title)
        row.addWidget(self.btnMin)
        row.addWidget(self.btnMax)
        row.addWidget(self.btnClose)

        # signals
        self.btnMin.clicked.connect(lambda: self.window().showMinimized())
        self.btnMax.clicked.connect(self._toggle_max_restore)
        self.btnClose.clicked.connect(lambda: self.window().close())

        self._refresh_max_icon()
        wnd = self.window()
        if hasattr(wnd, "windowStateChanged"):
            wnd.windowStateChanged.connect(  # pragma: no cover - platform dependent
                lambda *_: self._refresh_max_icon()
            )

    def _refresh_max_icon(self) -> None:
        self.btnMax.setText("❐" if self.window().isMaximized() else "□")

    def _toggle_max_restore(self):
        w = self.window()
        if w.isMaximized():
            w.showNormal()
        else:
            w.showMaximized()
        self._refresh_max_icon()

    # Drag-to-move
    def mouseDoubleClickEvent(self, e):  # double-click to toggle
        if e.button() == Qt.MouseButton.LeftButton:
            self._toggle_max_restore()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._mouse_pos = e.globalPosition().toPoint()

            # Use Qt 6 system move if available
            wh = self.window().windowHandle()
            try:
                wh.startSystemMove()
            except Exception:
                pass
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # Fallback manual move if startSystemMove is unavailable
        if self._mouse_pos is not None:
            delta = e.globalPosition().toPoint() - self._mouse_pos
            w = self.window()
            w.move(w.pos() + delta)
            self._mouse_pos = e.globalPosition().toPoint()
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._mouse_pos = None
        super().mouseReleaseEvent(e)


class FramelessMainWindow(QMainWindow):
    """
    A window with a custom TitleBar and content container.
    - Uses FramelessWindowHint to hide the OS bar.
    - Title bar matches app background; no icon shown.
    - Provides a .set_content(widget) convenience.
    """
    def __init__(self, title: str = "better5e", parent=None):
        super().__init__(parent)
        self.setObjectName("FramelessMainWindow")
        self.setWindowTitle(title)
        # Hide native chrome
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )
        # Central layout: TitleBar on top, content below
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        host = QWidget(self)
        host.setLayout(root)
        super().setCentralWidget(host)

        self.titleBar = TitleBar(self, title=title)
        root.addWidget(self.titleBar)

        self._contentHost = QFrame(self)
        self._contentHost.setObjectName("WindowContent")
        root.addWidget(self._contentHost)

        # Optional: system menu accelerator (Alt+Space)
        actMenu = QAction(self)
        actMenu.setShortcut("Alt+Space")
        actMenu.triggered.connect(lambda: None)  # no-op for now
        self.addAction(actMenu)

    def set_content(self, w: QWidget) -> None:
        # Replace content widget
        lay = self._contentHost.layout()
        if lay is None:
            lay = QVBoxLayout(self._contentHost)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(0)
        else:
            while lay.count():
                item = lay.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        lay.addWidget(w)
