import sys

from PyQt6.QtWidgets import QApplication

from features.camera_window import CameraWindow


def run_app() -> int:
    """Инициализация и запуск Qt-приложения."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    cam = CameraWindow()
    cam.show()

    return app.exec()
