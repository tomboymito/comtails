# Рекомендуемые версии окружения

## Минимум для запуска текущего проекта

- **OS**: Linux/macOS/WSL2
- **Python**: 3.10+
- **CMake**: 3.16+
- **C++ компилятор**: GCC 11+ или Clang 14+

Python-пакеты (runtime):
- `numpy`
- `astropy`
- `requests`
- `pygame`

## Рекомендуемо для этапа переписывания (расчёты)

- **Python**: 3.11
- **CMake**: 3.28+
- **GCC**: 13+
- **CUDA Toolkit**: 12.4+ (когда перейдём к GPU-этапу)
- **NVIDIA Driver**: совместимый с CUDA 12.4+
- **Rust** (для будущего GUI): 1.77+

## Быстрый чек версий

```bash
python --version
cmake --version
g++ --version
rustc --version
nvcc --version
```

## Полная проверка проекта

```bash
./scripts/verify_project.sh
```

Скрипт проверяет:
1. сборку и тесты нативного `comtails_core`;
2. parity benchmark + regression checker;
3. `py_compile` для Python-части;
4. наличие базовых Python-зависимостей.


## Проверено в текущем окружении CI/контейнера

- Python 3.12.12
- CMake 3.28.3
- GCC 13.3.0
- Rust 1.89.0
- `nvcc` в данном окружении отсутствует (CUDA toolkit не установлен)
