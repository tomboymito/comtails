#!/usr/bin/env python3
"""Построение русскоязычных графиков из CSV-артефактов COMTAILS.

Скрипт читает:
- output_cpp/flux.csv
- output_cpp/opt_depth.csv
- comtails_core/parity_dataset.csv

и сохраняет PNG-графики в каталог output_png/.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    import numpy as np
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(
        "Не хватает зависимостей для построения графиков: установите numpy и matplotlib. "
        f"Техническая причина: {exc}"
    )


def load_matrix_csv(path: Path) -> np.ndarray:
    """Загрузка двумерной матрицы из CSV в numpy-массив."""
    return np.loadtxt(path, delimiter=",")


def plot_heatmap(data: np.ndarray, title: str, cbar_label: str, out_path: Path, cmap: str = "inferno") -> None:
    """Построение тепловой карты (псевдоцвет) и сохранение в PNG."""
    plt.figure(figsize=(8, 6))
    img = plt.imshow(data, origin="lower", cmap=cmap, aspect="auto")
    plt.colorbar(img, label=cbar_label)
    plt.title(title)
    plt.xlabel("Пиксель X (плоскость неба)")
    plt.ylabel("Пиксель Y (плоскость неба)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def plot_parity_timing(parity_csv: Path, out_path: Path) -> None:
    """Построение графика времени расчёта по сценариям parity (small/medium/large)."""
    rows = np.genfromtxt(parity_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")

    scenarios = rows["scenario"]
    elapsed = rows["elapsed_ms"]

    plt.figure(figsize=(8, 5))
    plt.plot(scenarios, elapsed, marker="o", linewidth=2)
    plt.title("Время C++ Monte Carlo расчёта по parity-сценариям")
    plt.xlabel("Сценарий")
    plt.ylabel("Время, мс")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Построение PNG-графиков из CSV результатов COMTAILS")
    parser.add_argument("--flux-csv", type=Path, default=Path("output_cpp/flux.csv"))
    parser.add_argument("--opt-depth-csv", type=Path, default=Path("output_cpp/opt_depth.csv"))
    parser.add_argument("--parity-csv", type=Path, default=Path("comtails_core/parity_dataset.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("output_png"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    flux = load_matrix_csv(args.flux_csv)
    opt_depth = load_matrix_csv(args.opt_depth_csv)

    plot_heatmap(
        flux,
        "Фотометрическая карта потока пылевого хвоста",
        "Поток (отн. единицы)",
        args.out_dir / "flux_map.png",
        cmap="magma",
    )

    plot_heatmap(
        opt_depth,
        "Карта оптической толщины пылевого хвоста",
        "Оптическая толщина",
        args.out_dir / "opt_depth_map.png",
        cmap="viridis",
    )

    plot_parity_timing(args.parity_csv, args.out_dir / "parity_timing.png")

    print("PNG-графики сохранены в:", args.out_dir)


if __name__ == "__main__":
    main()
