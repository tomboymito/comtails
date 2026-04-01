"""Точка входа COMTAILS для запуска астрофизической симуляции пылевого хвоста кометы."""
import os
import sys
import argparse

from simulation import SimulationController
from utils.version import print_version_info, print_citation_info
from utils.io_utils import reset_directory


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='COMTAILS Comet Dust Tail Simulation')

    parser.add_argument('--input-dir', type=str, default='input',
                        help='Directory containing input files')

    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory for output files')

    parser.add_argument('--config', type=str, default='TAIL_INPUTS.dat',
                        help='Main configuration file name')

    parser.add_argument('--dust-profile', type=str, default='dmdt_vel_power_rmin_rmax.dat',
                        help='Dust loss rate profile file name')

    parser.add_argument('--validate', action='store_true',
                        help='Validate results against expected values')

    parser.add_argument('--expected-afrho', type=float, default=10.5,
                        help='Expected Afrho value for validation')

    parser.add_argument('--expected-mag', type=float, default=8.07,
                        help='Expected magnitude for validation')

    parser.add_argument('--tolerance', type=float, default=0.1,
                        help='Validation tolerance (relative difference)')

    return parser.parse_args()


def main():
    """Run the COMTAILS simulation."""
    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    args = parse_arguments()

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    input_dir = args.input_dir
    required_files = [
        os.path.join(input_dir, args.config),
        os.path.join(input_dir, args.dust_profile)
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: Required input file '{file}' not found.")
            sys.exit(1)

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    print_version_info()

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    reset_directory(args.output_dir)

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    simulation = SimulationController()
    simulation.run(required_files)

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    if args.validate:
        validation_result = SimulationController.validate_results(
            os.path.join(args.output_dir, "afrho.dat"),
            args.expected_afrho,
            args.expected_mag,
            args.tolerance
        )

        if not validation_result:
            print("Validation failed!")
            sys.exit(1)

    # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
    print_version_info()
    print_citation_info()


if __name__ == "__main__":
    main()
