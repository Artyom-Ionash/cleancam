import os
from PIL import Image
from pathlib import Path

def create_multiscale_ico():
    # Определяем пути относительно корня проекта
    project_root = Path(__file__).parent.parent.parent
    png_path = project_root / "assets" / "icon.png"
    ico_path = project_root / "assets" / "icon.ico"

    # 1. Проверяем наличие исходного PNG
    if not png_path.exists():
        print(f"Ошибка: Исходный файл {png_path} не найден.")
        return

    # 2. Удаляем старый ICO, если он существует (Стирание)
    if ico_path.exists():
        try:
            os.remove(ico_path)
            print(f"Старая иконка удалена: {ico_path}")
        except Exception as e:
            print(f"Не удалось удалить старый файл: {e}")
            return

    # 3. Генерация нового файла
    try:
        img = Image.open(png_path)

        # Оптимальный набор размеров для Windows (без 512)
        # Включаем 24 и 48 для корректного отображения при разном масштабировании системы
        sizes = sorted(set([(2**i, 2**i) for i in range(4, 9)] + [(24, 24), (48, 48)]))

        # Сохраняем новый многослойный контейнер
        img.save(ico_path, format='ICO', sizes=sizes)
        print(f"Успех: Новая иконка создана и сохранена в {ico_path}")
        print(f"Включенные размеры: {[f'{w}x{h}' for w, h in sizes]}")

    except Exception as e:
        print(f"Ошибка при создании иконки: {e}")

if __name__ == "__main__":
    create_multiscale_ico()
