from typing import Callable

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QSizePolicy

from core.python.paths import resource_path
from ui.atoms.frameless_window import AspectRatioFramelessWindow
from ui.atoms.tray_icon import AppTrayIcon
from ui.molecules.camera_controls import CameraControls


class CameraWindowUI(AspectRatioFramelessWindow):
    """Организм: Главное окно. Собирает атомы и молекулы воедино."""

    def __init__(
        self,
        on_switch: Callable[[], None],
        on_rotate: Callable[[], None],
        on_close: Callable[[], None],
        get_frame: Callable,
        get_aspect_ratio: Callable[[], float],
    ):
        # Инициализация базового функционала безрамочного окна
        super().__init__(get_aspect_ratio)

        self.get_frame = get_frame
        self.on_close_callback = on_close
        self.initial_resize_done = False

        self._setup_layouts(on_switch, on_rotate)
        self._setup_tray()

        # Таймер обновления UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(16)  # ~60 FPS

    def _setup_layouts(self, on_switch, on_rotate):
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Слой 0: Видео
        # Используем стандартный QLabel, так как вся логика мыши теперь в окне
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ВАЖНО: Делаем QLabel прозрачным для мыши, чтобы события
        # проваливались в базовый класс AspectRatioFramelessWindow
        self.video_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.video_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        main_layout.addWidget(self.video_label, 0, 0)

        # Слой 1: Оверлей управления
        self.controls = CameraControls(
            parent=self,
            on_switch=on_switch,
            on_rotate=on_rotate,
            on_close=self.close_application,
        )
        main_layout.addWidget(
            self.controls, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

    def _setup_tray(self):
        icon_path = resource_path("assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.tray_icon = AppTrayIcon(
            parent=self,
            on_toggle=self.toggle_visibility,
            on_quit=self.close_application,
            icon_path=icon_path,
        )
        self.tray_icon.show()

    def update_ui(self):
        frame = self.get_frame()
        if frame is None:
            return

        h, w, ch = frame.shape

        if not self.initial_resize_done:
            default_width = 320
            target_height = int(default_width / self.get_aspect_ratio())
            self.resize(default_width, target_height)
            self.initial_resize_done = True

        q_img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)

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
        if self.on_close_callback:
            self.on_close_callback()
        QApplication.quit()

    def closeEvent(self, a0):
        if a0:
            a0.ignore()
        self.hide()
