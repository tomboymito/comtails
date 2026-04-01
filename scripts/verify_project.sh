#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ok() { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }

ok "Проверка нативного ядра (CMake/CTest)"
cmake -S comtails_core -B comtails_core/build >/tmp/comtails_cmake_config.log 2>&1
cmake --build comtails_core/build >/tmp/comtails_cmake_build.log 2>&1
ctest --test-dir comtails_core/build --output-on-failure >/tmp/comtails_ctest.log 2>&1
ok "Нативные тесты пройдены"

ok "Обновление parity dataset"
./comtails_core/build/comtails_core_bench_parity_dataset comtails_core/parity_dataset.csv >/tmp/comtails_parity_bench.log 2>&1
./comtails_core/build/comtails_core_check_parity_regression comtails_core/parity_dataset.csv >/tmp/comtails_parity_check.log 2>&1
ok "Parity benchmark + regression check пройдены"

ok "Синтаксическая проверка Python-модулей"
python -m py_compile benchmarks/stage1_profile.py main.py simulation.py models/dust_tail.py
ok "Python py_compile пройден"

ok "Проверка доступности зависимостей Python runtime"
python - <<'PY'
import importlib
mods = ["numpy", "astropy", "requests", "pygame"]
missing = []
for m in mods:
    try:
        importlib.import_module(m)
    except Exception:
        missing.append(m)
if missing:
    print("MISSING:", ",".join(missing))
else:
    print("MISSING:")
PY

MISSING_LINE=$(python - <<'PY'
import importlib
mods=["numpy","astropy","requests","pygame"]
missing=[]
for m in mods:
    try:
        importlib.import_module(m)
    except Exception:
        missing.append(m)
print(','.join(missing))
PY
)

if [[ -n "$MISSING_LINE" ]]; then
  warn "Для полного runtime-запуска main.py не хватает пакетов: $MISSING_LINE"
  warn "Установите их и затем запустите: python main.py"
else
  ok "Все базовые Python-зависимости обнаружены"
fi

ok "Проверка завершена"
