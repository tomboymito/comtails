#!/usr/bin/env python3
"""Профилировщик этапа 1 для вычислительных ядер COMTAILS.

Скрипт профилирует наиболее ресурсоёмкие численные блоки без внешних сервисов
(JPL Horizons, FITS I/O и GUI). Это первый практический шаг
в переписывании вычислительного слоя.
"""

from __future__ import annotations

import argparse
import cProfile
import json
import os
import pstats
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from constants import FLOAT_TYPE
from models.dust_tail import DustTail, dust_tail_worker


@dataclass
class MockComet:
    xarr: np.ndarray
    yarr: np.ndarray
    zarr: np.ndarray
    vxarr: np.ndarray
    vyarr: np.ndarray
    vzarr: np.ndarray
    trueanarr: np.ndarray
    ec: FLOAT_TYPE
    half_per: FLOAT_TYPE
    orb_per: FLOAT_TYPE


class MockConfig:
    """Конфигурация с ровно теми полями, которые нужны пылевым ядрам."""

    def __init__(self, ntimes: int, nsizes: int, nevent: int, nx: int, ny: int):
        self.nx = nx
        self.ny = ny

        self.iprn = 0
        self.igrapho = 0
        self.iejec_mode = 1
        self.isun = 0

        self.ntimes = ntimes
        self.nsizes = nsizes
        self.nevent = nevent

        self.per_jd = FLOAT_TYPE(2460000.5)
        self.end_jd = FLOAT_TYPE(self.per_jd + 50.0)
        self.deltat = FLOAT_TYPE(0.5)

        self.times = np.linspace(self.per_jd - 20.0, self.end_jd, ntimes, dtype=FLOAT_TYPE)

        self.dtime = np.array([-100.0, -20.0, 0.0, 20.0, 80.0], dtype=FLOAT_TYPE)
        self.dmdtlog = np.array([2.3, 2.6, 2.8, 2.5, 2.0], dtype=FLOAT_TYPE)
        self.powera = np.array([-3.5, -3.6, -3.7, -3.6, -3.4], dtype=FLOAT_TYPE)
        self.velfac = np.array([0.7, 0.9, 1.0, 0.9, 0.8], dtype=FLOAT_TYPE)
        self.radiomin = np.array([1.0e-6] * 5, dtype=FLOAT_TYPE)
        self.radiomax = np.array([5.0e-4] * 5, dtype=FLOAT_TYPE)
        self.ninputs = len(self.dtime)

        self.pden = FLOAT_TYPE(1000.0)
        self.v0 = FLOAT_TYPE(120.0)
        self.gamma = FLOAT_TYPE(0.5)
        self.kappa = FLOAT_TYPE(-0.5)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.psang = FLOAT_TYPE(0.0)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.helio_matrix = np.eye(3, dtype=FLOAT_TYPE)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.delta = FLOAT_TYPE(1.3)
        self.nmpar = FLOAT_TYPE(0.0)
        self.nmpar1 = FLOAT_TYPE(1.0)
        self.nmpar2 = FLOAT_TYPE(0.0)
        self.nmpar3 = FLOAT_TYPE(0.0)
        self.nmpar4 = FLOAT_TYPE(0.0)
        self.nmpar5 = FLOAT_TYPE(1.0)
        self.nmpar6 = FLOAT_TYPE(0.0)
        self.nmpar7 = FLOAT_TYPE(0.0)
        self.nmpar8 = FLOAT_TYPE(0.0)

        self.tc = FLOAT_TYPE(self.end_jd - self.per_jd)
        self.rcobs = FLOAT_TYPE(1.2)
        self.thetacobs = FLOAT_TYPE(0.5)

        # Комментарий (RU): астрофизическая логика и назначение описаны в коде.
        self.nmin = FLOAT_TYPE(-2.5e6)
        self.nmax = FLOAT_TYPE(2.5e6)
        self.mmin = FLOAT_TYPE(-2.5e6)
        self.mmax = FLOAT_TYPE(2.5e6)
        self.augx = FLOAT_TYPE(nx / (self.nmax - self.nmin))
        self.augy = FLOAT_TYPE(ny / (self.mmax - self.mmin))

        self.cte_part = FLOAT_TYPE(1.0)
        self.grdsiz = FLOAT_TYPE(1500.0)
        self.inuc = nx // 2
        self.jnuc = ny // 2


def build_mock_comet(times: np.ndarray, per_jd: FLOAT_TYPE) -> MockComet:
    """Построить синтетическую, но гладкую траекторию кометы."""
    phase = (times - per_jd) / FLOAT_TYPE(20.0)
    theta = phase * FLOAT_TYPE(2.0 * np.pi)

    radius = FLOAT_TYPE(1.2)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = FLOAT_TYPE(0.05) * np.sin(theta * FLOAT_TYPE(0.5))

    dt = FLOAT_TYPE(times[1] - times[0]) if len(times) > 1 else FLOAT_TYPE(1.0)
    vx = np.gradient(x, dt).astype(FLOAT_TYPE)
    vy = np.gradient(y, dt).astype(FLOAT_TYPE)
    vz = np.gradient(z, dt).astype(FLOAT_TYPE)

    return MockComet(
        xarr=x.astype(FLOAT_TYPE),
        yarr=y.astype(FLOAT_TYPE),
        zarr=z.astype(FLOAT_TYPE),
        vxarr=vx,
        vyarr=vy,
        vzarr=vz,
        trueanarr=theta.astype(FLOAT_TYPE),
        ec=FLOAT_TYPE(0.5),
        half_per=FLOAT_TYPE(500.0),
        orb_per=FLOAT_TYPE(1000.0),
    )


def profile_worker(config: MockConfig, comet: MockComet, profile_path: Path) -> dict:
    profiler = cProfile.Profile()
    profiler.enable()
    t0 = time.perf_counter()
    result = dust_tail_worker(0, config.ntimes, comet, config)
    elapsed = time.perf_counter() - t0
    profiler.disable()

    profiler.dump_stats(str(profile_path))

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumtime")
    top = []
    for func, stat in list(stats.stats.items()):
        cc, nc, tt, ct, callers = stat
        if ct <= 0.0:
            continue
        filename, lineno, fn_name = func
        top.append({
            "функция": f"{Path(filename).name}:{fn_name}:{lineno}",
            "накопленное_время_с": ct,
            "чистое_время_с": tt,
            "ncalls": nc,
        })
    top.sort(key=lambda x: x["накопленное_время_с"], reverse=True)

    non_zero_flux = int(np.count_nonzero(result["flux_local"]))
    return {
        "время_ядра_с": elapsed,
        "total_mass_local": float(result["total_mass_local"]),
        "opt_depth_nuc_local": float(result["opt_depth_nuc_local"]),
        "non_zero_flux_pixels": non_zero_flux,
        "топ_функций": top[:15],
    }


def benchmark_convolution(nx: int, ny: int, sfwhm: float) -> dict:
    dummy_cfg = type("DummyCfg", (), {"nx": nx, "ny": ny})
    dust_tail = DustTail(dummy_cfg)

    flux = np.random.default_rng(1234).random((nx, ny), dtype=FLOAT_TYPE)
    t0 = time.perf_counter()
    dust_tail.apply_convolution(flux, FLOAT_TYPE(sfwhm))
    elapsed = time.perf_counter() - t0

    return {
        "время_свертки_с": elapsed,
        "сумма_потока_после_свертки": float(np.sum(flux)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Профилировщик базового вычислительного baseline (этап 1)")
    parser.add_argument("--ntimes", type=int, default=24)
    parser.add_argument("--nsizes", type=int, default=12)
    parser.add_argument("--nevent", type=int, default=150)
    parser.add_argument("--nx", type=int, default=160)
    parser.add_argument("--ny", type=int, default=160)
    parser.add_argument("--sfwhm", type=float, default=3.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/output/stage1"))
    args = parser.parse_args()

    np.random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    config = MockConfig(args.ntimes, args.nsizes, args.nevent, args.nx, args.ny)
    comet = build_mock_comet(config.times, config.per_jd)

    profile_path = args.output_dir / "dust_tail_worker.prof"
    worker_info = profile_worker(config, comet, profile_path)
    conv_info = benchmark_convolution(args.nx, args.ny, args.sfwhm)

    summary = {
        "временная_метка_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "параметры": {
            "ntimes": args.ntimes,
            "nsizes": args.nsizes,
            "nevent": args.nevent,
            "nx": args.nx,
            "ny": args.ny,
            "sfwhm": args.sfwhm,
            "seed": args.seed,
        },
        "результаты": {
            **worker_info,
            **conv_info,
        },
        "артефакты": {
            "cprofile": str(profile_path),
        },
    }

    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    print(f"[этап1] Сводка сохранена в {summary_path}")
    print(f"[этап1] Профиль cProfile сохранён в {profile_path}")


if __name__ == "__main__":
    main()
