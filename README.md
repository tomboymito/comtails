# COMTAILS — симулятор пылевого хвоста кометы

COMTAILS — это полнофункциональная Python-реализация программы для моделирования пылевых хвостов комет. Проект развивает исходный код на FORTRAN 77, созданный Fernando Moreno (IAA-CSIC), и предлагает более чистую объектно-ориентированную архитектуру, повышенную численную устойчивость и улучшенную визуализацию. Портирование последовательной FORTRAN-версии в параллельную Python-версию выполнено Rafael Morales и Nicolás Robles (IAA-CSIC).

Оригинальные репозитории с FORTRAN-версиями:
- FORTRAN serial: https://github.com/FernandoMorenoDanvila/COMTAILS/tree/FORTRAN_SERIAL
- FORTRAN MPI parallel: https://github.com/FernandoMorenoDanvila/COMTAILS/tree/FORTRAN_PARALLEL

## Описание

COMTAILS строит реалистичные модели пылевых хвостов комет, рассчитывая динамику пылевых частиц под действием солнечной гравитации и давления солнечного излучения. На выходе формируются научные изображения, пригодные для сопоставления с реальными наблюдениями.

### Ключевые возможности

- Монте-Карло моделирование динамики пылевых частиц
- Высокоточные орбитальные расчёты с решателями уравнения Кеплера
- Поддержка разных моделей выброса пыли (изотропный, в сторону Солнца, активные области)
- Интеграция с JPL Horizons для получения точных эфемерид
- Наложение звёздного поля из Gaia EDR3
- Экспорт FITS-изображений для научного анализа
- Визуализация частиц через pygame
- Поддержка multiprocessing для ускорения вычислений
- Расчёт параметров Afρ и блеска комы

## Установка

### Требования

- Python 3.8+
- NumPy
- AstroPy
- PyGame (для визуализации)
- Requests (для API JPL Horizons)

### Шаги установки

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/username/comtails.git
   cd comtails
   ```

2. Установите зависимости:
   ```bash
   pip install numpy astropy pygame requests
   ```

## Использование

### Базовый запуск

```bash
python main.py
```

По умолчанию запускается GUI-окно: в нём есть кнопка **«Запустить расчёт»**, статус выполнения, а после окончания — итоговые параметры и предпросмотр графиков прямо внутри окна.

### Запуск с пользовательской конфигурацией

```bash
python main.py --input-dir custom_inputs --config my_config.dat --dust-profile my_profile.dat
```

Если нужно запустить старый консольный режим (без GUI-окна):

```bash
python main.py --cli
```

Если нужно отключить итоговое меню и генерацию итогового PNG-результата:

```bash
python main.py --cli --no-menu
```

Если нужно дополнительно открыть отдельное окно итоговой “менюшки” после расчёта (в CLI-режиме):

```bash
python main.py --cli --open-menu-window
```

## Конфигурационные файлы

COMTAILS использует два основных входных файла:

1. **Основной конфигурационный файл** (по умолчанию: `TAIL_INPUTS.dat`):
   - параметры кометы;
   - геометрия наблюдений;
   - настройки моделирования;
   - диапазон дат, размер сетки изображения и физические параметры пыли.

2. **Профиль темпа потери пыли** (по умолчанию: `dmdt_vel_power_rmin_rmax.dat`):
   - темп пылеобразования;
   - коэффициенты скоростей выброса;
   - показатели степенного распределения размеров;
   - диапазоны размеров частиц как функция времени.

## Выходные файлы

Результаты сохраняются в каталоге `output`:

- `tail_sdu.fits`: яркость пылевого хвоста (в единицах интенсивности солнечного диска)
- `tail_mag.fits`: яркость пылевого хвоста (mag/arcsec²)
- `OPT_DEPTH.fits`: карта оптической толщины
- `afrho.dat`: параметр Afρ как функция времени
- `dust_particles.png`: визуализация положений пылевых частиц (если включено)
- `dustlossrate.dat`: темп пылепотерь как функция времени
- Дополнительные файлы в зависимости от выбранной конфигурации

## Структура кода

- `main.py`: точка входа
- `simulation.py`: главный контроллер моделирования
- `config.py`: управление параметрами и входными данными
- `constants.py`: физические и математические константы
- `models/comet.py`: модель кометы и орбитальные параметры
- `models/dust_tail.py`: модель пылевого хвоста (Монте-Карло)
- `orbital/heliorbit.py`: гелиоцентрические орбитальные расчёты
- `orbital/orbit_solver.py`: решатели уравнения Кеплера
- `visualization/star_field.py`: генерация/обработка звёздного поля
- `visualization/plot_handler.py`: инструменты визуализации
- `horizons/horizons_client.py`: клиент API JPL Horizons
- `fits/fits_writer.py`: запись FITS-файлов

## Лицензия

См. файл `LICENSE` (MIT).

## Цитирование

Если вы используете код в научной работе, укажите:

> The model results are based on a python implementation, performed by Rafael Morales and Nicolás Robles of the Instituto de Astrofísica de Andalucía, from the original FORTRAN serial code written by Fernando Moreno (Moreno, 2025).

И добавьте в список литературы:

> Moreno, F. (2025). COMetary dust TAIL Simulator (COMTAILS): A computer code to generate comet dust tail brightness images. Astronomy and Astrophysics, Volume:695(2025), Article:A263.

## Благодарности

Также уместно поблагодарить:

- NASA/JPL-Caltech за систему эфемерид Horizons
- ESA/Gaia за звёздные каталоги
