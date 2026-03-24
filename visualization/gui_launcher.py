"""
Графический запуск COMTAILS: окно с кнопкой старта, статусом и результатами.
"""
from __future__ import annotations

import os
import traceback

import pygame as pg

from app_runner import run_simulation_pipeline


class ComtailsGUI:
    def __init__(self, args):
        self.args = args
        self.width, self.height = 1500, 930
        self.status_lines: list[str] = ["Нажмите «Запустить расчёт» для старта моделирования."]
        self.result_lines: list[str] = []
        self.outputs = {}
        self.summary_surface = None
        self.particle_surface = None
        self.is_running_calc = False

    def _append_status(self, message: str) -> None:
        self.status_lines.append(str(message))
        self.status_lines = self.status_lines[-16:]

    def _start_calculation(self, screen) -> None:
        if self.is_running_calc:
            return

        self.status_lines = ["Запуск расчёта..."]
        self.result_lines = []
        self.outputs = {}
        self.summary_surface = None
        self.particle_surface = None
        self.is_running_calc = True

        # Обновим экран перед длительным расчётом, чтобы пользователь видел статус.
        self._draw_ui(screen, force_message="Расчёт выполняется... подождите.")
        pg.display.flip()

        try:
            results, outputs = run_simulation_pipeline(self.args, status_callback=self._append_status)
            self.outputs = outputs
            self.result_lines = [
                "Итоговые параметры:",
                f"Afρ (м): {results.get('afrho', 0.0):.6g}",
                f"Afρ(0°) (м): {results.get('afrho_0', 0.0):.6g}",
                f"m_R: {results.get('mag', 0.0):.6g}",
                f"Суммарная масса пыли (кг): {results.get('total_dust_mass', 0.0):.6g}",
            ]
            self.status_lines.append("Готово: расчёт завершён успешно.")
            self._load_result_images()
        except Exception as e:
            self.status_lines.append("Ошибка выполнения расчёта:")
            tb = traceback.format_exc(limit=2)
            for line in f"{e}\n{tb}".splitlines():
                self.status_lines.append(line)
            self.status_lines = self.status_lines[-18:]
        finally:
            self.is_running_calc = False

    def _load_result_images(self) -> None:
        summary_path = self.outputs.get("summary_image")
        particle_path = self.outputs.get("particle_image")
        if summary_path and os.path.exists(summary_path):
            image = pg.image.load(summary_path)
            self.summary_surface = pg.transform.smoothscale(image, (680, 420))
        if particle_path and os.path.exists(particle_path):
            image = pg.image.load(particle_path)
            self.particle_surface = pg.transform.smoothscale(image, (680, 420))

    def _draw_ui(self, screen, force_message: str | None = None) -> None:
        title_font = pg.font.SysFont("Arial", 34, bold=True)
        text_font = pg.font.SysFont("Arial", 24)
        small_font = pg.font.SysFont("Arial", 20)
        run_button = pg.Rect(30, 90, 360, 58)

        screen.fill((15, 19, 30))

        title = title_font.render("COMTAILS: GUI-меню запуска и просмотра результатов", True, (235, 235, 235))
        screen.blit(title, (30, 24))

        button_color = (42, 133, 77) if not self.is_running_calc else (90, 90, 90)
        pg.draw.rect(screen, button_color, run_button, border_radius=10)
        button_text = "Запустить расчёт" if not self.is_running_calc else "Расчёт выполняется..."
        screen.blit(text_font.render(button_text, True, (250, 250, 250)), (48, 105))

        screen.blit(text_font.render("Статус выполнения:", True, (176, 224, 230)), (30, 170))
        y = 205
        for line in self.status_lines[-16:]:
            screen.blit(small_font.render(line[:95], True, (230, 230, 230)), (35, y))
            y += 24

        if force_message:
            screen.blit(small_font.render(force_message, True, (255, 255, 120)), (35, min(y + 8, 590)))

        screen.blit(text_font.render("Результаты:", True, (255, 228, 181)), (30, 620))
        y = 655
        for line in self.result_lines:
            screen.blit(small_font.render(line, True, (250, 250, 250)), (35, y))
            y += 28

        if self.summary_surface is not None:
            screen.blit(self.summary_surface, (790, 80))
            screen.blit(small_font.render("Итоговая менюшка (PNG)", True, (220, 220, 220)), (790, 56))
        if self.particle_surface is not None:
            screen.blit(self.particle_surface, (790, 510))
            screen.blit(small_font.render("График частиц", True, (220, 220, 220)), (790, 486))

        hint = "Esc — выход. Для нового расчёта нажмите кнопку снова."
        screen.blit(small_font.render(hint, True, (170, 170, 170)), (30, 890))

    def run(self) -> None:
        pg.init()
        pg.font.init()

        screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("COMTAILS — GUI запуск моделирования")
        run_button = pg.Rect(30, 90, 360, 58)
        running = True
        clock = pg.time.Clock()

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if run_button.collidepoint(event.pos):
                        self._start_calculation(screen)

            self._draw_ui(screen)

            pg.display.flip()
            clock.tick(30)

        pg.quit()
