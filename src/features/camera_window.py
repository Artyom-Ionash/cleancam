from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QIcon, QImage, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget

from core.python.paths import resource_path
from lib.video.camera_logic import CameraManager
from ui.atoms.tray_icon import AppTrayIcon
from ui.atoms.video_label import VideoLabel
from ui.molecules.camera_controls import CameraControls


class CameraWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.logic = CameraManager()
        self._resizing = False
        self._resize_edge = 0
        self.old_pos = None
        self.initial_resize_done = False

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

        # UI Элементы
        self.video_label = VideoLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Молекула управления (Overlay)
        self.controls = CameraControls(
            parent=self,
            on_switch=self.logic.switch_camera,
            on_rotate=self.logic.rotate_camera,
            on_close=self.close_application,
        )

        # Трей
        icon_path = resource_path("assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.tray_icon = AppTrayIcon(
            parent=self,
            on_toggle=self.toggle_visibility,
            on_quit=self.close_application,
            icon_path=icon_path,
        )
        self.tray_icon.show()

        # Таймер обновления UI (теперь легкий, т.к. кадры идут из очереди)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(16)  # ~60 FPS

    def update_ui(self):
        frame = self.logic.get_frame()
        if frame is None:
            return

        h, w, ch = frame.shape
        if not self.initial_resize_done:
            default_width = 320
            target_height = int(default_width / self.logic.aspect_ratio)
            self.resize(default_width, target_height)
            self.initial_resize_done = True

        q_img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)
        self.video_label.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, a0):
        """Обновление геометрии оверлея при изменении размера окна."""
        super().resizeEvent(a0)
        self.controls.setGeometry(self.width() - 130, 10, 120, 40)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def enterEvent(self, event):
        self.controls.show_controls()
        super().enterEvent(event)

    def leaveEvent(self, a0):
        self.controls.hide_controls()
        super().leaveEvent(a0)

    def close_application(self):
        self.logic.release()
        QApplication.quit()

    def closeEvent(self, a0):
        if a0:
            a0.ignore()
        self.hide()

    def mousePressEvent(self, a0: QMouseEvent | None):
        if a0 is None:
            return
        pos = a0.position().toPoint()
        edge = self.video_label._get_edge_flags(pos)

        if a0.button() == Qt.MouseButton.LeftButton:
            if edge:
                self._resizing = True
                self._resize_edge = edge
                self._drag_start_pos = a0.globalPosition().toPoint()
                self._drag_start_geometry = self.geometry()
            else:
                self.old_pos = a0.globalPosition().toPoint()

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if a0 is None:
            return
        if self._resizing:
            delta = a0.globalPosition().toPoint() - self._drag_start_pos
            g = self._drag_start_geometry
            new_rect = QRect(g)

            if self._resize_edge & 2:
                new_w = max(100, g.width() + delta.x())
                new_rect.setWidth(new_w)
                new_rect.setHeight(int(new_w / self.logic.aspect_ratio))
            elif self._resize_edge & 1:
                new_w = max(100, g.width() - delta.x())
                new_rect.setLeft(g.right() - new_w)
                new_rect.setHeight(int(new_w / self.logic.aspect_ratio))
            elif self._resize_edge & 8:
                new_h = max(100, g.height() + delta.y())
                new_rect.setHeight(new_h)
                new_rect.setWidth(int(new_h * self.logic.aspect_ratio))
            elif self._resize_edge & 4:
                new_h = max(100, g.height() - delta.y())
                new_rect.setTop(g.bottom() - new_h)
                new_rect.setWidth(int(new_h * self.logic.aspect_ratio))
            self.setGeometry(new_rect)
        elif self.old_pos is not None:
            delta = a0.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = a0.globalPosition().toPoint()

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        self._resizing = False
        self._resize_edge = 0
        self.old_pos = None
