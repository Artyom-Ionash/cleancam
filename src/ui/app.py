import sys

from PyQt6.QtWidgets import QApplication

from features.main_window import CleanCam


def run_app() -> int:
    """Инициализация и запуск Qt-приложения."""
    app = QApplication(sys.argv)

    # Чтобы приложение не закрывалось при скрытии окна в трей
    app.setQuitOnLastWindowClosed(False)

    cam = CleanCam()
    cam.show()

    return app.exec()
