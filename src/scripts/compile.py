import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def run_build():
    base_path = Path(__file__).parent.parent.resolve()
    project_root = base_path.parent

    # Пути
    main_script = str(base_path / "main.py")
    icon_path = str(project_root / "assets" / "icon.ico")
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"

    # Предварительная очистка для чистоты эксперимента
    for path in [build_dir, dist_dir]:
        if path.exists():
            shutil.rmtree(path)

    params = [
        main_script,
        '--name=CleanCam',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        f'--icon={icon_path}', # Теперь путь к реальному ICO
        f'--specpath={str(build_dir)}',
        f'--distpath={str(dist_dir)}',
        f'--workpath={str(build_dir)}',
        f'--add-data={str(project_root / "assets")}{os.pathsep}assets',
        # Исключения (по желанию)
        '--exclude-module=PyQt6.QtNetwork',
        '--exclude-module=PyQt6.QtWebEngine',
    ]

    PyInstaller.__main__.run(params)

if __name__ == "__main__":
    run_build()
