"""Визуализация распределения пылевых частиц в плоскости неба."""
import os
import numpy as np
import pygame as pg
from constants import FLOAT_TYPE


class PlotHandler:
    """
    Class to handle visualization for the dust tail simulation using Pygame.

    This class provides methods to visualize dust particle positions,
    create informative plots, and save images to disk.
    """

    def __init__(self, nmin, nmax, mmin, mmax, filename="output/dust_particles.png",
                width=1200, height=1200, bg_color=(0, 0, 0)):
        """
        Initialize Pygame-based visualization system.

        Args:
            nmin, nmax (float): X-axis limits in km
            mmin, mmax (float): Y-axis limits in km
            filename (str): Path to save the output image
            width (int): Width of the output image in pixels
            height (int): Height of the output image in pixels
            bg_color (tuple): Background color as RGB tuple
        """
        self.available = False
        self.nmin = FLOAT_TYPE(nmin)
        self.nmax = FLOAT_TYPE(nmax)
        self.mmin = FLOAT_TYPE(mmin)
        self.mmax = FLOAT_TYPE(mmax)
        self.filename = filename
        self.particles = []   # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.colors = []      # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.sizes = []       # Комментарий (RU): астрофизическая логика и назначение описаны в коде.

        try:
            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            pg.init()
            pg.font.init()

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.width = width
            self.height = height

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.margin = 100
            self.plot_width = self.width - 2 * self.margin
            self.plot_height = self.height - 2 * self.margin

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.screen = pg.Surface((self.width, self.height))
            self.screen.fill(bg_color)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.x_scale = self.plot_width / (self.nmax - self.nmin)
            self.y_scale = self.plot_height / (self.mmax - self.mmin)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.bg_color = bg_color
            self.axis_color = (150, 150, 150)
            self.grid_color = (50, 50, 50)
            self.text_color = (255, 255, 255)
            self.particle_color = (255, 255, 255)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.title_font = pg.font.SysFont('Arial', 24, bold=True)
            self.label_font = pg.font.SysFont('Arial', 20)
            self.small_font = pg.font.SysFont('Arial', 16)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            self.available = True

            print(f"Plot handler initialized with dimensions: {self.width}x{self.height}")

        except Exception as e:
            print(f"Error initializing PlotHandler: {e}")
            self.available = False

    def draw_axes(self):
        """
        Draw coordinate axes with labels.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            return False

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        rect = pg.Rect(self.margin, self.margin, self.plot_width, self.plot_height)
        pg.draw.rect(self.screen, self.axis_color, rect, 1)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        x_ticks = np.linspace(self.nmin, self.nmax, 9)
        for tick in x_ticks:
            x_pos = self.margin + (tick - self.nmin) * self.x_scale

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            pg.draw.line(self.screen, self.axis_color,
                        (x_pos, self.height - self.margin),
                        (x_pos, self.height - self.margin + 5), 1)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            if tick == 0:
                label = "0"
            else:
                label = f"{tick:.1e}"

            text = self.small_font.render(label, True, self.text_color)
            self.screen.blit(text, (x_pos - text.get_width()//2,
                                   self.height - self.margin + 10))

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            pg.draw.line(self.screen, self.grid_color,
                        (x_pos, self.margin),
                        (x_pos, self.height - self.margin), 1)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        y_ticks = np.linspace(self.mmin, self.mmax, 9)
        for tick in y_ticks:
            y_pos = self.height - self.margin - (tick - self.mmin) * self.y_scale

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            pg.draw.line(self.screen, self.axis_color,
                        (self.margin, y_pos),
                        (self.margin - 5, y_pos), 1)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            if tick == 0:
                label = "0"
            else:
                label = f"{tick:.1e}"

            text = self.small_font.render(label, True, self.text_color)
            self.screen.blit(text, (self.margin - 10 - text.get_width(),
                                   y_pos - text.get_height()//2))

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            pg.draw.line(self.screen, self.grid_color,
                        (self.margin, y_pos),
                        (self.width - self.margin, y_pos), 1)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        x_label = self.label_font.render("Projected distance on RA axis [km]", True, self.text_color)
        self.screen.blit(x_label, (self.width//2 - x_label.get_width()//2,
                                 self.height - self.margin//2))

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        y_label = self.label_font.render("Projected distance on DEC axis [km]", True, self.text_color)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        y_label_rotated = pg.Surface((y_label.get_height(), y_label.get_width()), pg.SRCALPHA)
        for y in range(y_label.get_height()):
            for x in range(y_label.get_width()):
                y_label_rotated.set_at((y_label.get_height() - y - 1, x),
                                      y_label.get_at((x, y)))

        self.screen.blit(y_label_rotated, (self.margin//4,
                                         self.height//2 - y_label.get_width()//2))

        return True

    def plot_particles(self):
        """
        Plot all stored particles on the surface.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available or not self.particles:
            return False

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.draw_axes()

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        for i, (npar, mpar) in enumerate(self.particles):
            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            x = int(self.margin + (npar - self.nmin) * self.x_scale)
            y = int(self.height - self.margin - (mpar - self.mmin) * self.y_scale)

            # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
            if (self.margin <= x < self.width - self.margin and
                self.margin <= y < self.height - self.margin):
                # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
                pg.draw.circle(self.screen, self.colors[i], (x, y), self.sizes[i])

        return True

    def add_nucleus_marker(self):
        """
        Add a marker for the nucleus position.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            return False

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        nx = self.margin + (0 - self.nmin) * self.x_scale
        ny = self.height - self.margin - (0 - self.mmin) * self.y_scale

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        pg.draw.circle(self.screen, (255, 0, 0), (int(nx), int(ny)), 5)
        pg.draw.line(self.screen, (255, 0, 0), (int(nx-7), int(ny)), (int(nx+7), int(ny)), 1)
        pg.draw.line(self.screen, (255, 0, 0), (int(nx), int(ny-7)), (int(nx), int(ny+7)), 1)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        text = self.small_font.render("Nucleus", True, (255, 0, 0))
        self.screen.blit(text, (int(nx) + 10, int(ny) - 10))

        return True

    def save_image(self, filename=None):
        """
        Save the current plot to a PNG file.

        Args:
            filename (str): Optional override for the filename

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            return False

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        output_file = filename if filename else self.filename

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.plot_particles()

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.add_nucleus_marker()

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        try:
            pg.image.save(self.screen, output_file)
            print(f"Saved particle plot to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def add_particle(self, npar, mpar, color=None, size=1):
        """
        Add a particle to the plot.

        Args:
            npar (float): X coordinate in km
            mpar (float): Y coordinate in km
            color (tuple): Optional RGB color tuple
            size (int): Optional particle size in pixels

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            return False

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.particles.append((FLOAT_TYPE(npar), FLOAT_TYPE(mpar)))
        self.colors.append(color if color else self.particle_color)
        self.sizes.append(size)

        return True

    def close(self):
        """
        Close the Pygame system.

        Returns:
            bool: True if successful, False otherwise
        """
        if self.available:
            pg.quit()
            self.available = False
            return True

        return False


