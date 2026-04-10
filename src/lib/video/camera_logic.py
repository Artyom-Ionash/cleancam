import threading
import time
from typing import Optional

import cv2
import numpy as np


class CameraManager:
    def __init__(self):
        self.camera_indices: list[int] = self._get_available_cameras()
        self.current_camera_idx: int = 0
        self.aspect_ratio: float = 1.0

        # Потокобезопасные переменные
        self._lock: threading.Lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._running: bool = True
        self._switch_requested: bool = False
        self._rotation_angle: int = 0

        # Запуск фонового потока
        self._thread: threading.Thread = threading.Thread(
            target=self._capture_loop, daemon=True
        )
        self._thread.start()

    def _get_available_cameras(self) -> list[int]:
        available: list[int] = []
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available if available else [0]

    def switch_camera(self) -> None:
        """Асинхронно запрашивает смену камеры."""
        self.camera_indices = self._get_available_cameras()
        self.current_camera_idx = (self.current_camera_idx + 1) % len(
            self.camera_indices
        )
        self._switch_requested = True

    def rotate_camera(self) -> None:
        with self._lock:
            self._rotation_angle = (self._rotation_angle + 90) % 360

    def _capture_loop(self) -> None:
        """Бесконечный цикл чтения кадров в фоновом потоке."""
        cap: Optional[cv2.VideoCapture] = None

        def open_camera():
            nonlocal cap
            if cap:
                cap.release()
            device_idx = self.camera_indices[self.current_camera_idx]
            cap = cv2.VideoCapture(device_idx, cv2.CAP_DSHOW)

        open_camera()

        while self._running:
            if self._switch_requested:
                open_camera()
                self._switch_requested = False

            if cap is None or not cap.isOpened():
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            with self._lock:
                angle = self._rotation_angle

            # Обработка кадра
            mode_map = {
                90: cv2.ROTATE_90_CLOCKWISE,
                180: cv2.ROTATE_180,
                270: cv2.ROTATE_90_COUNTERCLOCKWISE,
            }
            if angle in mode_map:
                frame = cv2.rotate(frame, mode_map[angle])

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]

            with self._lock:
                self.aspect_ratio = float(w) / float(h) if h > 0 else 1.0
                self._latest_frame = frame

        if cap:
            cap.release()

    def get_frame(self) -> Optional[np.ndarray]:
        """Мгновенно возвращает последний готовый кадр (не блокирует UI)."""
        with self._lock:
            return self._latest_frame

    def release(self) -> None:
        """Останавливает поток и освобождает ресурсы."""
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
