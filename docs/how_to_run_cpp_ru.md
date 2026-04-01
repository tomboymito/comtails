# Как запускать C++ часть проекта и как устроена структура

## Важное уточнение

`python main.py` запускает исходный Python-контур симуляции.

Если нужен именно C++ путь, используйте `comtails_core`:
- unit-тесты ядра;
- parity-бенчмарки;
- synthetic C++ расчёт с генерацией карт потока и оптической толщины.

## Структура проекта (с астрофизическим назначением)

- `comtails_core/include/comtails_core.h` — C ABI расчётного ядра.
- `comtails_core/src/core_cpu.cpp` — нативные CPU-реализации (интерполяция `dM/dt`, свёртка фотометрии, Monte Carlo шаги).
- `comtails_core/tests/test_core_cpu.cpp` — тесты численной корректности.
- `comtails_core/tools/benchmark_parity_dataset.cpp` — parity-сценарии small/medium/large.
- `comtails_core/tools/check_parity_regression.cpp` — regression-контроль метрик parity CSV.
- `comtails_core/tools/run_synthetic_tail.cpp` — синтетический C++ расчёт и выгрузка `flux.csv`/`opt_depth.csv`.

## Полный запуск C++ конвейера

```bash
./scripts/run_cpp_pipeline.sh
```

Что делает скрипт:
1. CMake configure/build;
2. CTest;
3. parity benchmark + regression check;
4. synthetic C++ run с выходными картами в `output_cpp/`.

## Ручной запуск C++ программ

```bash
cmake -S comtails_core -B comtails_core/build
cmake --build comtails_core/build

# Тесты
ctest --test-dir comtails_core/build --output-on-failure

# Parity-бенчмарк
./comtails_core/build/comtails_core_bench_parity_dataset comtails_core/parity_dataset.csv

# Regression-проверка
./comtails_core/build/comtails_core_check_parity_regression comtails_core/parity_dataset.csv

# Синтетический астрофизический расчёт (C++)
./comtails_core/build/comtails_core_run_synthetic_tail 200000
```

## Что появится после C++ synthetic run

- `output_cpp/flux.csv` — фотометрическая карта распределения потока пылевого хвоста;
- `output_cpp/opt_depth.csv` — карта оптической толщины в плоскости неба.


## Как получить PNG-графики из CSV

После C++ расчёта выполните:

```bash
python scripts/plot_results_ru.py
```

Будут созданы:
- `output_png/flux_map.png`
- `output_png/opt_depth_map.png`
- `output_png/parity_timing.png`

## Как просматривать CSV

Варианты:
1. В текстовом/табличном виде:
   - VS Code (встроенный просмотр CSV),
   - LibreOffice Calc / Excel.
2. В виде изображений (тепловые карты):
   - через `python scripts/plot_results_ru.py`.
3. В Jupyter Notebook:
   - `pandas.read_csv(...)` + `matplotlib`/`seaborn` для интерактивной визуализации.
