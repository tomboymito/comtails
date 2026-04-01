# comtails_core — нативное астрофизическое расчётное ядро (CPU baseline)

`comtails_core` — это нативный C++ слой, который переносит наиболее ресурсоёмкие
участки моделирования пылевого хвоста из Python в высокопроизводительный CPU-контур,
подготовленный к дальнейшему CUDA-переносу.

## Реализованные вычислительные блоки

- `comtails_interp5_cpu` — интерполяция профиля пылепроизводства `dM/dt`.
- `comtails_convolution_cpu` — гауссова свёртка фотометрической матрицы яркости.
- `comtails_accumulate_particles_cpu` — аккумуляция вклада частиц в карту потока и оптической толщины.
- `comtails_sample_isotropic_velocity_cpu` — детерминированный изотропный отбор скоростей выброса.
- `comtails_monte_carlo_step_cpu` — batched Monte Carlo шаг (семплирование + аккумуляция).
- `comtails_monte_carlo_step_v2_cpu` — Monte Carlo шаг с физически корректной нормировкой `/nevent`.

## Сборка и тестирование

```bash
cmake -S comtails_core -B comtails_core/build
cmake --build comtails_core/build
ctest --test-dir comtails_core/build --output-on-failure
```

## Бенчмарки

### 1) Быстрый Monte Carlo бенчмарк

```bash
./comtails_core/build/comtails_core_bench_monte_carlo
./comtails_core/build/comtails_core_bench_monte_carlo 500000
```

### 2) Набор parity-сценариев (small/medium/large)

```bash
./comtails_core/build/comtails_core_bench_parity_dataset
./comtails_core/build/comtails_core_bench_parity_dataset parity_dataset.csv
```

### 3) Regression-проверка parity CSV

```bash
./comtails_core/build/comtails_core_check_parity_regression comtails_core/parity_dataset.csv
```

## Научная преемственность и авторство

- Исходная физическая модель COMTAILS/Fortran: Fernando Moreno (IAA-CSIC).
- Python-реализация: Rafael Morales и Nicolás Robles (IAA-CSIC).
- Русификация и высокопроизводительное переписывание: инициатор текущей линии проекта (см. `docs/AUTHORS_RU.md`).

## Следующий шаг

Полный перенос расширенного CPU event-loop в CUDA-ядра с контролем численного паритета
по фиксированным seed и parity-метрикам.
