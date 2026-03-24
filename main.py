"""
Main entry point for COMTAILS simulation.

This module provides the entry point for running the comet dust tail simulation.
It uses the refactored object-oriented design to improve upon the original
COMTAILS.for Fortran 77 code by Fernando Moreno IAA-CSIC.
"""
import sys
import argparse

from app_runner import run_simulation_pipeline
from visualization.gui_launcher import ComtailsGUI


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='COMTAILS — моделирование пылевого хвоста кометы')

    parser.add_argument('--input-dir', type=str, default='input',
                        help='Каталог со входными файлами')

    parser.add_argument('--output-dir', type=str, default='output',
                        help='Каталог для выходных файлов')

    parser.add_argument('--config', type=str, default='TAIL_INPUTS.dat',
                        help='Имя основного конфигурационного файла')

    parser.add_argument('--dust-profile', type=str, default='dmdt_vel_power_rmin_rmax.dat',
                        help='Имя файла профиля пылепотерь')

    parser.add_argument('--validate', action='store_true',
                        help='Проверить результаты относительно ожидаемых значений')

    parser.add_argument('--expected-afrho', type=float, default=10.5,
                        help='Ожидаемое значение Afρ для проверки')

    parser.add_argument('--expected-mag', type=float, default=8.07,
                        help='Ожидаемая звёздная величина для проверки')

    parser.add_argument('--tolerance', type=float, default=0.1,
                        help='Допуск проверки (относительное отклонение)')
    parser.add_argument('--no-menu', action='store_true',
                        help='Не выводить итоговое меню вычислений')
    parser.add_argument('--open-menu-window', action='store_true',
                        help='Открыть графическое окно с итоговой менюшкой результатов')
    parser.add_argument('--cli', action='store_true',
                        help='Запуск без GUI-окна (только консольный режим)')

    return parser.parse_args()


def main():
    """Run COMTAILS in GUI (default) or CLI mode."""
    args = parse_arguments()

    if args.cli:
        try:
            run_simulation_pipeline(args)
        except Exception as e:
            print(f"Ошибка запуска в CLI-режиме: {e}")
            sys.exit(1)
    else:
        gui = ComtailsGUI(args)
        gui.run()


if __name__ == "__main__":
    main()
