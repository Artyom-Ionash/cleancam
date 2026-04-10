import cv2
import numpy as np


class CameraManager:
    def __init__(self):
        self.cap = None
        self.rotation_angle = 0
        self.camera_indices = self._get_available_cameras()
        self.current_camera_idx = 0
        self.aspect_ratio = 1.0

    def _get_available_cameras(self):
        available = []
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available if available else [0]

    def switch_camera(self):
        self.camera_indices = self._get_available_cameras()
        self.current_camera_idx = (self.current_camera_idx + 1) % len(
            self.camera_indices
        )
        if self.cap:
            self.cap.release()
            self.cap = None

    def rotate_camera(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360

    def get_frame(self) -> np.ndarray | None:
        """Возвращает обработанный кадр (BGR -> RGB) или None."""
        if self.cap is None:
            device_idx = self.camera_indices[self.current_camera_idx]
            self.cap = cv2.VideoCapture(device_idx, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = None
                return None

        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.cap = None
            return None

        # Поворот
        mode_map = {
            90: cv2.ROTATE_90_CLOCKWISE,
            180: cv2.ROTATE_180,
            270: cv2.ROTATE_90_COUNTERCLOCKWISE,
        }
        if self.rotation_angle in mode_map:
            frame = cv2.rotate(frame, mode_map[self.rotation_angle])

        # Конвертация BGR -> RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        self.aspect_ratio = w / h

        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
