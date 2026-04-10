from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from ui.atoms.button import HoverButton


class CameraControls(QWidget):
    """Молекула: Панель кнопок управления камерой."""

    def __init__(self, parent=None, on_switch=None, on_rotate=None, on_close=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.btn_switch = HoverButton("📷")
        self.btn_rotate = HoverButton("↺")
        self.btn_close = HoverButton("✕")

        if on_switch:
            self.btn_switch.clicked.connect(on_switch)
        if on_rotate:
            self.btn_rotate.clicked.connect(on_rotate)
        if on_close:
            self.btn_close.clicked.connect(on_close)

        layout.addWidget(self.btn_switch)
        layout.addWidget(self.btn_rotate)
        layout.addWidget(self.btn_close)

    def show_controls(self):
        self.btn_switch.show()
        self.btn_rotate.show()
        self.btn_close.show()

    def hide_controls(self):
        self.btn_switch.hide()
        self.btn_rotate.hide()
        self.btn_close.hide()
