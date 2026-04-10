import sys

from PyQt6.QtWidgets import QApplication

from features.camera_controller import CameraController


def run_app() -> int:
    """Инициализация и запуск Qt-приложения."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    controller = CameraController()
    controller.run()

    return app.exec()
