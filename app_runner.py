"""
Общий запуск пайплайна COMTAILS для CLI и GUI.
"""
import os
from typing import Callable, Dict, Any, Tuple

from simulation import SimulationController
from utils.version import print_version_info, print_citation_info
from utils.io_utils import reset_directory
from visualization.result_menu import print_result_menu, save_result_photo, show_result_menu_window


def run_simulation_pipeline(args, status_callback: Callable[[str], None] | None = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Выполнить полный расчёт и вернуть результаты + пути к файлам результатов.
    """

    def emit(message: str) -> None:
        print(message)
        if status_callback:
            status_callback(message)

    input_dir = args.input_dir
    required_files = [
        os.path.join(input_dir, args.config),
        os.path.join(input_dir, args.dust_profile)
    ]

    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Обязательный входной файл не найден: {file}")

    emit("Инициализация COMTAILS...")
    print_version_info()

    emit("Подготовка выходного каталога...")
    reset_directory(args.output_dir)

    emit("Запуск численного моделирования...")
    simulation = SimulationController()
    results = simulation.run(required_files)

    summary_image = os.path.join(args.output_dir, "итог_расчета.png")
    particle_image = os.path.join(args.output_dir, "dust_particles.png")

    if not args.no_menu:
        emit("Формирование итогового меню и PNG-резюме...")
        print_result_menu(results)
        save_result_photo(results, summary_image, particle_image)
        if args.open_menu_window:
            show_result_menu_window(results, particle_image)

    if args.validate:
        emit("Проверка результатов...")
        validation_result = SimulationController.validate_results(
            os.path.join(args.output_dir, "afrho.dat"),
            args.expected_afrho,
            args.expected_mag,
            args.tolerance
        )
        if not validation_result:
            raise RuntimeError("Проверка результатов не пройдена.")

    emit("Расчёт завершён.")
    print_version_info()
    print_citation_info()

    outputs = {
        "summary_image": summary_image,
        "particle_image": particle_image,
        "afrho_file": os.path.join(args.output_dir, "afrho.dat"),
    }
    return results, outputs
