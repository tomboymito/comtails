# Статус проекта: что работает, а что требует донастройки

Дата проверки: 2026-04-01

## Короткий ответ

- **Да, вычислительный контур (native CPU baseline) работает стабильно**: сборка, тесты, parity benchmark и regression check проходят.
- **Нет, не всё готово для полноценного runtime-запуска `main.py` в текущем окружении**, потому что отсутствуют Python-зависимости (`numpy`, `astropy`, `requests`, `pygame`).

## Что проверено и прошло

1. Сборка и тесты `comtails_core` (CMake/CTest).
2. Обновление `parity_dataset.csv` и regression-проверка parity-метрик.
3. Синтаксическая проверка Python-модулей (`py_compile`).

## Что ещё нужно для полного запуска симуляции

Установить Python-пакеты:

```bash
pip install numpy astropy requests pygame
```

После этого выполнить:

```bash
python main.py
```

## Команда полной проверки

```bash
./scripts/verify_project.sh
```

Скрипт даёт честный итог: что прошло, а что заблокировано окружением.
