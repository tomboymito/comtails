"""
Русскоязычное меню итогов моделирования и генерация итогового изображения.
"""
import os
from typing import Dict, Any

import pygame as pg


def _build_result_surface(results: Dict[str, Any], width: int = 1400, height: int = 900,
                          particle_plot_file: str = "output/dust_particles.png") -> pg.Surface:
    """
    Построить поверхность с итоговым меню и результатами.
    """
    surface = pg.Surface((width, height))
    surface.fill((16, 18, 28))

    title_font = pg.font.SysFont("Arial", 36, bold=True)
    text_font = pg.font.SysFont("Arial", 24)
    small_font = pg.font.SysFont("Arial", 20)

    title = title_font.render("COMTAILS — итог расчёта пылевого хвоста", True, (240, 240, 240))
    surface.blit(title, (40, 30))

    y = 100
    steps = results.get("calculation_steps", [])
    subtitle = text_font.render("Выполненные этапы вычислений:", True, (173, 216, 230))
    surface.blit(subtitle, (40, y))
    y += 40

    for idx, step in enumerate(steps, start=1):
        line = small_font.render(f"{idx:02d}. {step}", True, (220, 220, 220))
        surface.blit(line, (60, y))
        y += 28

    y += 12
    final_lines = [
        f"Afρ (м): {results.get('afrho', 0.0):.6g}",
        f"Afρ(0°) (м): {results.get('afrho_0', 0.0):.6g}",
        f"m_R: {results.get('mag', 0.0):.6g}",
        f"Суммарная масса пыли (кг): {results.get('total_dust_mass', 0.0):.6g}",
    ]
    summary_title = text_font.render("Итоговые параметры:", True, (255, 228, 181))
    surface.blit(summary_title, (40, y))
    y += 40
    for line_text in final_lines:
        line = text_font.render(line_text, True, (255, 245, 238))
        surface.blit(line, (60, y))
        y += 36

    hint = small_font.render("Закройте окно или нажмите Esc/Enter", True, (170, 170, 170))
    surface.blit(hint, (40, height - 40))

    if os.path.exists(particle_plot_file):
        try:
            particle_plot = pg.image.load(particle_plot_file)
            particle_plot = pg.transform.smoothscale(particle_plot, (620, 620))
            surface.blit(particle_plot, (740, 160))
        except Exception:
            pass

    return surface


def print_result_menu(results: Dict[str, Any]) -> None:
    """
    Вывести в консоль краткое меню с этапами вычислений и итогами.
    """
    steps = results.get("calculation_steps", [])
    print("\n=== МЕНЮ ВЫЧИСЛЕНИЙ COMTAILS ===")
    for idx, step in enumerate(steps, start=1):
        print(f"{idx:02d}. {step}")

    print("\n--- Итоговые астрофизические параметры ---")
    print(f"Afρ (м): {results.get('afrho', 0.0):.6g}")
    print(f"Afρ(0°) (м): {results.get('afrho_0', 0.0):.6g}")
    print(f"m_R: {results.get('mag', 0.0):.6g}")
    print(f"Суммарная масса пыли (кг): {results.get('total_dust_mass', 0.0):.6g}")
    print("===================================\n")


def save_result_photo(results: Dict[str, Any], output_file: str,
                      particle_plot_file: str = "output/dust_particles.png") -> bool:
    """
    Создать итоговое PNG-изображение с меню вычислений и основными результатами.
    """
    pygame_was_init = pg.get_init()
    font_was_init = pg.font.get_init()

    try:
        if not pygame_was_init:
            pg.init()
        if not font_was_init:
            pg.font.init()

        surface = _build_result_surface(results, particle_plot_file=particle_plot_file)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        pg.image.save(surface, output_file)
        print(f"Итоговое изображение результата сохранено: {output_file}")
        return True
    except Exception as e:
        print(f"Не удалось создать итоговое изображение результата: {e}")
        return False
    finally:
        if not font_was_init and pg.font.get_init():
            pg.font.quit()
        if not pygame_was_init and pg.get_init():
            pg.quit()


def show_result_menu_window(results: Dict[str, Any],
                            particle_plot_file: str = "output/dust_particles.png") -> bool:
    """
    Открыть графическое окно с итоговой «менюшкой» результатов.
    """
    pygame_was_init = pg.get_init()
    font_was_init = pg.font.get_init()

    try:
        if not pygame_was_init:
            pg.init()
        if not font_was_init:
            pg.font.init()

        width, height = 1400, 900
        screen = pg.display.set_mode((width, height))
        pg.display.set_caption("COMTAILS — меню результатов")

        surface = _build_result_surface(results, width=width, height=height,
                                        particle_plot_file=particle_plot_file)

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key in (pg.K_ESCAPE, pg.K_RETURN):
                    running = False

            screen.blit(surface, (0, 0))
            pg.display.flip()

        return True
    except Exception as e:
        print(f"Не удалось открыть графическое окно меню результатов: {e}")
        return False
    finally:
        if not font_was_init and pg.font.get_init():
            pg.font.quit()
        if not pygame_was_init and pg.get_init():
            pg.quit()
