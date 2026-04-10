from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QLabel


class VideoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._parent = parent
        self.edge_margin = 15

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

    def mouseMoveEvent(self, ev: QMouseEvent | None):
        if ev is None:
            return

        parent = self.parent()
        # Если мы сейчас НЕ ресайзим, просто показываем, какой курсор БУДЕТ, если нажать
        # Если ресайзим — оставляем тот, что выбрали при нажатии
        if parent is not None and not getattr(parent, "_resizing", False):
            edge = self._get_edge_flags(ev.position().toPoint())
            if edge:
                cursors = {
                    1: Qt.CursorShape.SizeHorCursor,  # Left
                    2: Qt.CursorShape.SizeHorCursor,  # Right
                    4: Qt.CursorShape.SizeVerCursor,  # Top
                    8: Qt.CursorShape.SizeVerCursor,  # Bottom
                    5: Qt.CursorShape.SizeFDiagCursor,  # Top-Left (1+4)
                    6: Qt.CursorShape.SizeBDiagCursor,  # Top-Right (2+4)
                    9: Qt.CursorShape.SizeBDiagCursor,  # Bottom-Left (1+8)
                    10: Qt.CursorShape.SizeFDiagCursor,  # Bottom-Right (2+8)
                }
                self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(ev)
