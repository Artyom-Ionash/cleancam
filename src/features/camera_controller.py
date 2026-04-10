from lib.video.camera_logic import CameraManager
from ui.organisms.camera_ui import CameraWindowUI


class CameraController:
    """
    Контроллер (Медиатор).
    Связывает бизнес-логику (CameraManager) с представлением (CameraWindowUI).
    Гарантированно не содержит зависимостей от PyQt6.
    """

    def __init__(self):
        self.logic = CameraManager()

        # UI получает только коллбеки (никакого прямого связывания логики внутри UI)
        self.ui = CameraWindowUI(
            on_switch=self.logic.switch_camera,
            on_rotate=self.logic.rotate_camera,
            on_close=self.logic.release,
            get_frame=self.logic.get_frame,
            get_aspect_ratio=lambda: self.logic.aspect_ratio,
        )

    def run(self):
        self.ui.show()
