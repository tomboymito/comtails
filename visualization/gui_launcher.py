"""
Графический запуск COMTAILS: окно с кнопкой старта, статусом и результатами.
"""
from __future__ import annotations

import os
import queue
import threading
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

        self.sim_thread: threading.Thread | None = None
        self.message_queue: queue.Queue = queue.Queue()
        self.is_running_calc = False

    def _enqueue(self, message: str) -> None:
        self.message_queue.put(("status", message))

    def _worker(self) -> None:
        try:
            results, outputs = run_simulation_pipeline(self.args, status_callback=self._enqueue)
            self.message_queue.put(("done", (results, outputs)))
        except Exception as e:
            tb = traceback.format_exc(limit=2)
            self.message_queue.put(("error", f"{e}\n{tb}"))

    def _start_calculation(self) -> None:
        if self.is_running_calc:
            return
        self.status_lines = ["Запуск расчёта..."]
        self.result_lines = []
        self.outputs = {}
        self.summary_surface = None
        self.particle_surface = None
        self.is_running_calc = True
        self.sim_thread = threading.Thread(target=self._worker, daemon=True)
        self.sim_thread.start()

    def _process_messages(self) -> None:
        while True:
            try:
                msg_type, payload = self.message_queue.get_nowait()
            except queue.Empty:
                break

            if msg_type == "status":
                self.status_lines.append(str(payload))
                self.status_lines = self.status_lines[-16:]
            elif msg_type == "done":
                results, outputs = payload
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
                self.is_running_calc = False
            elif msg_type == "error":
                self.status_lines.append("Ошибка выполнения расчёта:")
                for line in str(payload).splitlines():
                    self.status_lines.append(line)
                self.status_lines = self.status_lines[-18:]
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

    def run(self) -> None:
        pg.init()
        pg.font.init()

        screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("COMTAILS — GUI запуск моделирования")

        title_font = pg.font.SysFont("Arial", 34, bold=True)
        text_font = pg.font.SysFont("Arial", 24)
        small_font = pg.font.SysFont("Arial", 20)

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
                        self._start_calculation()

            self._process_messages()

            screen.fill((15, 19, 30))

            # Заголовок
            title = title_font.render("COMTAILS: GUI-меню запуска и просмотра результатов", True, (235, 235, 235))
            screen.blit(title, (30, 24))

            # Кнопка запуска
            button_color = (42, 133, 77) if not self.is_running_calc else (90, 90, 90)
            pg.draw.rect(screen, button_color, run_button, border_radius=10)
            button_text = "Запустить расчёт" if not self.is_running_calc else "Расчёт выполняется..."
            screen.blit(text_font.render(button_text, True, (250, 250, 250)), (48, 105))

            # Статусы
            screen.blit(text_font.render("Статус выполнения:", True, (176, 224, 230)), (30, 170))
            y = 205
            for line in self.status_lines[-16:]:
                screen.blit(small_font.render(line[:95], True, (230, 230, 230)), (35, y))
                y += 24

            # Итоги
            screen.blit(text_font.render("Результаты:", True, (255, 228, 181)), (30, 620))
            y = 655
            for line in self.result_lines:
                screen.blit(small_font.render(line, True, (250, 250, 250)), (35, y))
                y += 28

            # Изображения
            if self.summary_surface is not None:
                screen.blit(self.summary_surface, (790, 80))
                screen.blit(small_font.render("Итоговая менюшка (PNG)", True, (220, 220, 220)), (790, 56))
            if self.particle_surface is not None:
                screen.blit(self.particle_surface, (790, 510))
                screen.blit(small_font.render("График частиц", True, (220, 220, 220)), (790, 486))

            hint = "Esc — выход. Для нового расчёта нажмите кнопку снова."
            screen.blit(small_font.render(hint, True, (170, 170, 170)), (30, 890))

            pg.display.flip()
            clock.tick(30)

        pg.quit()
