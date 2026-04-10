import os
import shutil
from pathlib import Path

import PyInstaller.__main__
from PIL import Image


def generate_icon(png_path: Path, build_dir: Path) -> Path | None:
    """Генерирует .ico файл из .png и сохраняет его в папку build."""
    if not png_path.exists():
        print(f"⚠️ Предупреждение: Исходный файл {png_path} не найден.")
        return None

    # Убеждаемся, что папка build существует до запуска PyInstaller
    build_dir.mkdir(parents=True, exist_ok=True)

    ico_path = build_dir / "icon.ico"
    print(
        f"🖼 Генерация иконки: {png_path.name} -> {ico_path.relative_to(build_dir.parent)}"
    )

    try:
        img = Image.open(png_path)
        # Сохраняем с поддержкой нескольких размеров для корректного отображения в Windows
        img.save(
            ico_path,
            format="ICO",
            sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
        )
        return ico_path
    except Exception as e:
        print(f"❌ Ошибка при генерации иконки: {e}")
        return None


def run_build():
    project_root = Path(__file__).parent.parent.parent
    main_script = str(project_root / "src" / "main.py")

    build_dir = project_root / "build"
    dist_dir = project_root / "dist"

    # 1. Очистка предыдущих артефактов
    for path in [build_dir, dist_dir]:
        if path.exists():
            shutil.rmtree(path)

    # 2. Генерация иконки в build/
    png_path = project_root / "assets" / "icon.png"
    ico_path = generate_icon(png_path, build_dir)

    # 3. Настройка параметров PyInstaller
    params = [
        main_script,
        "--name=CleanCam",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--specpath={str(build_dir)}",
        f"--distpath={str(dist_dir)}",
        f"--workpath={str(build_dir)}",
        f"--add-data={str(project_root / 'assets')}{os.pathsep}assets",
        "--exclude-module=PyQt6.QtNetwork",
        "--exclude-module=PyQt6.QtWebEngine",
        # Добавьте эту строку для сборки плагинов изображений:
        "--collect-binaries=PyQt6",
    ]

    # Если иконка успешно создана, добавляем её к параметрам сборки
    if ico_path and ico_path.exists():
        params.append(f"--icon={str(ico_path)}")

    print("🚀 Запуск PyInstaller...")
    PyInstaller.__main__.run(params)


if __name__ == "__main__":
    run_build()
