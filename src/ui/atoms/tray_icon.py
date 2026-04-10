import os
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon


class AppTrayIcon(QSystemTrayIcon):
    """Компонент (Молекула): Системный трей с меню управления."""

    def __init__(
        self,
        parent=None,
        on_toggle: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
        icon_path: str | None = None,
    ):
        super().__init__(parent)
        self.on_toggle = on_toggle
        self.on_quit = on_quit

        # Безопасная установка иконки
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            if icon_path:
                print(f"⚠️ Внимание: Иконка не найдена по пути: {icon_path}")
            self.setIcon(QIcon(self._generate_default_pixmap()))

        self.setToolTip("CleanCam")

        # Формирование контекстного меню
        menu = QMenu()
        if show_action := menu.addAction("Показать/Скрыть"):
            show_action.triggered.connect(self._handle_toggle)
        if quit_action := menu.addAction("Выход"):
            quit_action.triggered.connect(self._handle_quit)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _handle_toggle(self):
        if self.on_toggle:
            self.on_toggle()

    def _handle_quit(self):
        if self.on_quit:
            self.on_quit()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._handle_toggle()

    @staticmethod
    def _generate_default_pixmap() -> QPixmap:
        """Рендер дефолтной иконки, если физический файл не найден."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)

        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(12, 12, 8, 8)
        painter.end()

        return pixmap
