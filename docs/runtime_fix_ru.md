# Что означает предупреждение про Python runtime-пакеты и как исправить

## Что означает предупреждение

Сообщение вида:

- `MISSING: numpy,astropy,requests,pygame`

означает, что в вашем текущем Python-окружении отсутствуют библиотеки,
которые нужны для полноценного запуска моделирования (`python main.py`).

Важно:
- это **не ошибка C++ ядра**;
- это **не провал тестов нативного контура**;
- это ограничение именно Python runtime-окружения.

## Почему при этом "проверка прошла"

Скрипт `./scripts/verify_project.sh` состоит из двух частей:

1. **Обязательная техническая проверка** (сборка C++, CTest, parity benchmark, regression check, py_compile) — должна пройти.
2. **Диагностика окружения Python runtime** — может выдать предупреждение, если пакеты не установлены.

Поэтому итог «прошёл с предупреждением» означает:
- вычислительный контур и тесты корректны;
- но для запуска полной астрофизической симуляции нужно установить Python-зависимости.

## Как исправить (рекомендуемый путь)

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy astropy requests pygame
```

После установки:

```bash
./scripts/verify_project.sh
python main.py
```

## Для Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install numpy astropy requests pygame
```

Далее:

```powershell
python main.py
```
