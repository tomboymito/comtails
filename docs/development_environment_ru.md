# Рекомендуемая IDE и окружение разработки

## Короткий ответ

Да, **VS Code отлично подходит** для этого проекта и для плана Python → C++/CUDA → Rust.

## Почему VS Code

- хорошо работает одновременно с Python, CMake/C++, CUDA и Rust;
- удобный встроенный терминал для `cmake`, `ctest`, `python`;
- расширения для отладки и профилирования;
- простая настройка devcontainer/Docker на следующих этапах.

## Рекомендуемые расширения VS Code

1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **C/C++** (ms-vscode.cpptools)
4. **CMake Tools** (ms-vscode.cmake-tools)
5. **CodeLLDB** (vadimcn.vscode-lldb) — по желанию
6. **rust-analyzer** (rust-lang.rust-analyzer) — для будущего GUI слоя
7. **Even Better TOML** (tamasfe.even-better-toml) — удобно для Rust/Cargo
8. **NVIDIA Nsight Visual Studio Code Edition** — когда дойдём до CUDA-профилирования

## Минимальный рабочий поток

```bash
# Проверка Python-части (синтаксис)
python -m py_compile benchmarks/stage1_profile.py main.py simulation.py models/dust_tail.py

# Сборка и тесты native core
cmake -S comtails_core -B comtails_core/build
cmake --build comtails_core/build
ctest --test-dir comtails_core/build --output-on-failure
```

## Рекомендация по профилям сборки

- для разработки: `Debug`
- для замеров производительности: `Release`

Пример:

```bash
cmake -S comtails_core -B comtails_core/build-release -DCMAKE_BUILD_TYPE=Release
cmake --build comtails_core/build-release
ctest --test-dir comtails_core/build-release --output-on-failure
```

## Что использовать кроме VS Code

- **CLion**: сильнее для C++/CMake в крупных кодовых базах;
- **PyCharm + CLion**: если хочется отдельные IDE для Python и C++;
- но для единого стека и быстрых итераций VS Code обычно оптимален.


## Авторство в документации

В описательных файлах проекта фиксируйте:
- исходных авторов научной модели и Python-реализации (IAA-CSIC);
- ваше авторство как автора русификации и переписывания на высокопроизводительные языки.

См. `docs/AUTHORS_RU.md`.


Дополнительно по версиям инструментов см. `docs/versions_ru.md`.
