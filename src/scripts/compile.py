import PyInstaller.__main__
import os
from pathlib import Path

def run_build():
    # Мы находимся в src/scripts/compile.py, main.py в src/main.py
    base_path = Path(__file__).parent.parent.resolve()
    project_root = base_path.parent
    main_script = str(base_path / "main.py")

    params = [
        main_script,
        '--name=CleanCam',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        f'--distpath={str(project_root / "dist")}',
        f'--workpath={str(project_root / "build")}',
    ]

    PyInstaller.__main__.run(params)
