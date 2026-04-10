import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    Получает абсолютный путь к ресурсам.
    """

    if meipass := getattr(sys, "_MEIPASS", None):
        base_path = Path(meipass)
    else:
        # Режим разработки: корень проекта.
        # Файл лежит в src/utils/paths.py, значит корень — 3 уровня вверх.
        base_path = Path(__file__).resolve().parents[3]

    # Строим путь
    full_path = (base_path / relative_path).absolute()

    # ДЕБАГ: Если иконка снова не видна, посмотрите в консоль
    if not full_path.exists():
        print(f"DEBUG: Путь к ресурсу не найден: {full_path}")

    return str(full_path)
