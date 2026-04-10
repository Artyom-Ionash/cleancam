import os
import sys

import cv2
from PyQt6.QtCore import QPoint, QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QImage, QMouseEvent, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QWidget,
)


def resource_path(relative_path):
    """Получает абсолютный путь к ресурсам.
    Работает и для разработки, и для PyInstaller."""
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Если запускаем через интерпретатор, берем путь относительно текущего файла
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class HoverButton(QPushButton):
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


class VideoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._parent = parent
        self.margin = 15

    def _get_edge_flags(self, pos: QPoint) -> int:
        edge = 0
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        if x < self.margin:
            edge |= 1
        if x > w - self.margin:
            edge |= 2
        if y < self.margin:
            edge |= 4
        if y > h - self.margin:
            edge |= 8
        return edge

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._parent._resizing:
            edge = self._get_edge_flags(event.position().toPoint())
            cursors = {
                1: Qt.CursorShape.SizeHorCursor,
                2: Qt.CursorShape.SizeHorCursor,
                4: Qt.CursorShape.SizeVerCursor,
                8: Qt.CursorShape.SizeVerCursor,
                5: Qt.CursorShape.SizeBDiagCursor,
                10: Qt.CursorShape.SizeBDiagCursor,
                6: Qt.CursorShape.SizeFDiagCursor,
                9: Qt.CursorShape.SizeFDiagCursor,
            }
            self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))
        super().mouseMoveEvent(event)


class CleanCam(QWidget):
    def __init__(self):
        super().__init__()
        self.cap = None
        self.rotation_angle = 0
        self.old_pos = None
        self._resizing = False
        self._resize_edge = 0
        self.aspect_ratio = 1.0
        self.initial_resize_done = False  # Флаг для первой подгонки размера

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

        # УБРАНО: self.resize(320, 480)

        self.video_label = VideoLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_close = HoverButton("✕", self)
        self.btn_close.clicked.connect(self.close_application)

        self.btn_rotate = HoverButton("↺", self)
        self.btn_rotate.clicked.connect(self.rotate_camera)

        # Инициализация трея
        self.setup_tray()

        icon_path = resource_path(os.path.join("assets", "icon.png"))
        self.setWindowIcon(QIcon(icon_path))
        self.tray_icon.setIcon(QIcon(icon_path))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)

        # Генерируем иконку "на лету" (белый круг с точкой)
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

        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("CleanCam")

        # Меню трея
        menu = QMenu()
        show_action = menu.addAction("Показать/Скрыть")
        show_action.triggered.connect(self.toggle_visibility)
        quit_action = menu.addAction("Выход")
        quit_action.triggered.connect(self.close_application)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visibility()

    def update_frame(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                return

        ret, frame = self.cap.read()
        if not ret:
            return

        mode_map = {
            90: cv2.ROTATE_90_CLOCKWISE,
            180: cv2.ROTATE_180,
            270: cv2.ROTATE_90_COUNTERCLOCKWISE,
        }
        if self.rotation_angle in mode_map:
            frame = cv2.rotate(frame, mode_map[self.rotation_angle])

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        self.aspect_ratio = w / h

        # --- ИСПРАВЛЕНИЕ: Первая подгонка размера ---
        if not self.initial_resize_done:
            default_width = 320
            target_height = int(default_width / self.aspect_ratio)
            self.resize(default_width, target_height)
            self.initial_resize_done = True
        # --------------------------------------------

        q_img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        # Используем KeepAspectRatio для чистоты отрисовки
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)
        self.video_label.setGeometry(0, 0, self.width(), self.height())

        margin, btn_s = 10, self.btn_close.width()
        self.btn_close.move(self.width() - btn_s - margin, margin)
        self.btn_rotate.move(self.width() - (btn_s * 2) - margin - 8, margin)

    def rotate_camera(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.resize(self.height(), self.width())

    def enterEvent(self, event):
        self.btn_close.show()
        self.btn_rotate.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_close.hide()
        self.btn_rotate.hide()
        super().leaveEvent(event)

    def close_application(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        QApplication.quit()

    def closeEvent(self, event):
        # При нажатии "X" или закрытии окна — просто скрываем в трей, если не нажата кнопка Выход
        event.ignore()
        self.hide()

    # --- Proportional Resize Logic ---
    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        edge = self.video_label._get_edge_flags(pos)
        if event.button() == Qt.MouseButton.LeftButton:
            if edge:
                self._resizing = True
                self._resize_edge = edge
                self._drag_start_pos = event.globalPosition().toPoint()
                self._drag_start_geometry = self.geometry()
            else:
                self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._resizing:
            delta = event.globalPosition().toPoint() - self._drag_start_pos
            g = self._drag_start_geometry
            new_rect = QRect(g)

            if self._resize_edge & 2:  # Right
                new_w = max(100, g.width() + delta.x())
                new_rect.setWidth(new_w)
                new_rect.setHeight(int(new_w / self.aspect_ratio))
            elif self._resize_edge & 1:  # Left
                new_w = max(100, g.width() - delta.x())
                new_rect.setLeft(g.right() - new_w)
                new_rect.setHeight(int(new_w / self.aspect_ratio))
            elif self._resize_edge & 8:  # Bottom
                new_h = max(100, g.height() + delta.y())
                new_rect.setHeight(new_h)
                new_rect.setWidth(int(new_h * self.aspect_ratio))
            elif self._resize_edge & 4:  # Top
                new_h = max(100, g.height() - delta.y())
                new_rect.setTop(g.bottom() - new_h)
                new_rect.setWidth(int(new_h * self.aspect_ratio))

            self.setGeometry(new_rect)
        elif self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._resizing = False
        self.old_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Чтобы приложение не закрывалось при скрытии окна
    app.setQuitOnLastWindowClosed(False)
    cam = CleanCam()
    cam.show()
    sys.exit(app.exec())
