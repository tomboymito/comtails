#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

cmake -S comtails_core -B comtails_core/build
cmake --build comtails_core/build
ctest --test-dir comtails_core/build --output-on-failure

./comtails_core/build/comtails_core_bench_parity_dataset comtails_core/parity_dataset.csv
./comtails_core/build/comtails_core_check_parity_regression comtails_core/parity_dataset.csv
./comtails_core/build/comtails_core_run_synthetic_tail 200000

echo "C++ конвейер выполнен успешно"
