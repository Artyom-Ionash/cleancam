import PyInstaller.__main__
import os
from pathlib import Path

def run_build():
    base_path = Path(__file__).parent.parent.resolve()
    project_root = base_path.parent

    # Путь к папке build в корне проекта
    build_dir = project_root / "build"

    params = [
        str(base_path / "main.py"),
        '--name=CleanCam',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        # Указываем PyInstaller класть .spec файл в папку build
        f'--specpath={str(build_dir)}',
        f'--distpath={str(project_root / "dist")}',
        f'--workpath={str(build_dir)}',
    ]

    PyInstaller.__main__.run(params)

if __name__ == "__main__":
    run_build()
