from typing import Callable

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget


class AspectRatioFramelessWindow(QWidget):
    """
    Атом: Безрамочное окно с поддержкой перетаскивания
    и изменения размера с сохранением пропорций.
    """

    def __init__(self, get_aspect_ratio: Callable[[], float]):
        super().__init__()
        self.get_aspect_ratio = get_aspect_ratio

        self._resizing = False
        self._resize_edge = 0
        self.old_pos = None
        self.edge_margin = 15

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setStyleSheet(
            "background-color: rgba(10, 10, 10, 1); border: 1px solid rgba(255, 255, 255, 10);"
        )

    def _get_edge_flags(self, pos: QPoint) -> int:
        edge = 0
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        if x < self.edge_margin:
            edge |= 1
        if x > w - self.edge_margin:
            edge |= 2
        if y < self.edge_margin:
            edge |= 4
        if y > h - self.edge_margin:
            edge |= 8
        return edge

    def mousePressEvent(self, a0: QMouseEvent | None):
        if a0 is None:
            return
        pos = a0.position().toPoint()
        edge = self._get_edge_flags(pos)

        if a0.button() == Qt.MouseButton.LeftButton:
            if edge:
                self._resizing = True
                self._resize_edge = edge
                self._drag_start_pos = a0.globalPosition().toPoint()
                self._drag_start_geometry = self.geometry()
            else:
                self.old_pos = a0.globalPosition().toPoint()
        super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if a0 is None:
            return

        # Обновление курсора при наведении на края
        if not self._resizing:
            edge = self._get_edge_flags(a0.position().toPoint())
            if edge:
                cursors = {
                    1: Qt.CursorShape.SizeHorCursor,
                    2: Qt.CursorShape.SizeHorCursor,
                    4: Qt.CursorShape.SizeVerCursor,
                    8: Qt.CursorShape.SizeVerCursor,
                    5: Qt.CursorShape.SizeFDiagCursor,
                    6: Qt.CursorShape.SizeBDiagCursor,
                    9: Qt.CursorShape.SizeBDiagCursor,
                    10: Qt.CursorShape.SizeFDiagCursor,
                }
                self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        # Логика ресайза
        if self._resizing:
            delta = a0.globalPosition().toPoint() - self._drag_start_pos
            g = self._drag_start_geometry
            new_rect = QRect(g)
            aspect_ratio = self.get_aspect_ratio()

            if self._resize_edge & 2:
                new_w = max(100, g.width() + delta.x())
                new_rect.setWidth(new_w)
                new_rect.setHeight(int(new_w / aspect_ratio))
            elif self._resize_edge & 1:
                new_w = max(100, g.width() - delta.x())
                new_rect.setLeft(g.right() - new_w)
                new_rect.setHeight(int(new_w / aspect_ratio))
            elif self._resize_edge & 8:
                new_h = max(100, g.height() + delta.y())
                new_rect.setHeight(new_h)
                new_rect.setWidth(int(new_h * aspect_ratio))
            elif self._resize_edge & 4:
                new_h = max(100, g.height() - delta.y())
                new_rect.setTop(g.bottom() - new_h)
                new_rect.setWidth(int(new_h * aspect_ratio))
            self.setGeometry(new_rect)

        # Логика перемещения окна
        elif self.old_pos is not None:
            delta = a0.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = a0.globalPosition().toPoint()

        super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        self._resizing = False
        self._resize_edge = 0
        self.old_pos = None
        super().mouseReleaseEvent(a0)
