from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class HoverButton(QPushButton):
    """Базовый UI-компонент кнопки с эффектом наведения (Атом)."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide()
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 150);
                color: rgba(255, 255, 255, 220);
                border-radius: 16px;
                font-size: 14px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 220);
                color: white;
            }
        """)
