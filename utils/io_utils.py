"""Служебные функции ввода/вывода для подготовки астрофизических данных модели."""
import os
import shutil

def reset_directory(dir_path):
    """
    Reset a directory by removing it and recreating it.

    Args:
        dir_path: Path to directory
    """
    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        print(f"Deleted existing directory: {dir_path}")

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    os.makedirs(dir_path)
    print(f"Created directory: {dir_path}")


