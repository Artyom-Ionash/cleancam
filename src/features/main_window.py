import cv2
from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QIcon, QImage, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget

from core.python.paths import resource_path
from ui.atoms.button import HoverButton
from ui.atoms.tray_icon import AppTrayIcon
from ui.atoms.video_label import VideoLabel


class CleanCam(QWidget):
    def __init__(self):
        super().__init__()
        self.cap = None
        self.rotation_angle = 0
        self.old_pos = None
        self._resizing = False
        self._resize_edge = 0
        self.aspect_ratio = 1.0
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

        self.btn_close = HoverButton("✕", self)
        self.btn_close.clicked.connect(self.close_application)

        self.btn_rotate = HoverButton("↺", self)
        self.btn_rotate.clicked.connect(self.rotate_camera)

        self.btn_switch = HoverButton("📷", self)
        self.btn_switch.clicked.connect(self.switch_camera)

        # Состояние камер
        self.camera_indices = self.get_available_cameras()
        self.current_camera_idx = 0

        # Настройка иконки окна и системного трея
        icon_path = resource_path("assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.tray_icon = AppTrayIcon(
            parent=self,
            on_toggle=self.toggle_visibility,
            on_quit=self.close_application,
            icon_path=icon_path,
        )
        self.tray_icon.show()

        # Инициализация цикла камеры
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def get_available_cameras(self):
        available = []
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available if available else [0]

    def switch_camera(self):
        self.camera_indices = self.get_available_cameras()
        self.current_camera_idx = (self.current_camera_idx + 1) % len(
            self.camera_indices
        )

        print(
            f"Переключение на камеру с индексом: {self.camera_indices[self.current_camera_idx]}"
        )

        if self.cap:
            self.cap.release()
            self.cap = None

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def update_frame(self):
        if self.cap is None:
            device_idx = self.camera_indices[self.current_camera_idx]
            self.cap = cv2.VideoCapture(device_idx, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = None
                return

        ret, frame = self.cap.read()

        if not ret:
            print("Сигнал потерян. Попытка переподключения...")
            if self.cap:
                self.cap.release()
            self.cap = None
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

        if not self.initial_resize_done:
            default_width = 320
            target_height = int(default_width / self.aspect_ratio)
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

        # Позиционирование кнопок управления
        margin, btn_s = 10, self.btn_close.width()
        self.btn_close.move(self.width() - btn_s - margin, margin)
        self.btn_rotate.move(self.width() - (btn_s * 2) - margin - 8, margin)
        self.btn_switch.move(self.width() - (btn_s * 3) - margin - 16, margin)

    def rotate_camera(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.resize(self.height(), self.width())

    def enterEvent(self, event):
        self.btn_close.show()
        self.btn_rotate.show()
        self.btn_switch.show()
        super().enterEvent(event)

    def leaveEvent(self, a0):
        self.btn_close.hide()
        self.btn_rotate.hide()
        self.btn_switch.hide()
        super().leaveEvent(a0)

    def close_application(self):
        if self.cap:
            self.cap.release()
            self.cap = None
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

        elif self.old_pos is not None:
            delta = a0.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = a0.globalPosition().toPoint()

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        self._resizing = False
        self._resize_edge = 0
        self.old_pos = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.video_label.setCursor(Qt.CursorShape.ArrowCursor)
