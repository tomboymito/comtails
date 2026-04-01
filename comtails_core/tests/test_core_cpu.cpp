#include "comtails_core.h"

#include <cmath>
#include <iostream>
#include <vector>

namespace {

bool approx(double a, double b, double eps = 1e-12) {
    return std::fabs(a - b) <= eps;
}

int test_interp() {
    const std::vector<double> dtime{-10.0, 0.0, 10.0};
    const std::vector<double> dmdtlog{1.0, 3.0, 5.0};
    const std::vector<double> powera{-3.0, -3.5, -4.0};
    const std::vector<double> velfac{0.5, 1.0, 1.5};
    const std::vector<double> rmin{1e-6, 2e-6, 3e-6};
    const std::vector<double> rmax{1e-4, 2e-4, 3e-4};

    auto left = comtails_interp5_cpu(-20.0, dtime.data(), dmdtlog.data(), powera.data(),
                                     velfac.data(), rmin.data(), rmax.data(), dtime.size());
    if (!approx(left.dmdtl, 1.0) || !approx(left.vfac, 0.5)) {
        std::cerr << "Ошибка: интерполяция (левая граница)\n";
        return 1;
    }

    auto mid = comtails_interp5_cpu(5.0, dtime.data(), dmdtlog.data(), powera.data(),
                                    velfac.data(), rmin.data(), rmax.data(), dtime.size());
    if (!approx(mid.dmdtl, 4.0) || !approx(mid.vfac, 1.25) || !approx(mid.power, -3.75)) {
        std::cerr << "Ошибка: интерполяция (внутренний сегмент)\n";
        return 1;
    }

    auto right = comtails_interp5_cpu(20.0, dtime.data(), dmdtlog.data(), powera.data(),
                                      velfac.data(), rmin.data(), rmax.data(), dtime.size());
    if (!approx(right.dmdtl, 5.0) || !approx(right.radmax, 3e-4)) {
        std::cerr << "Ошибка: интерполяция (правая граница)\n";
        return 1;
    }

    return 0;
}

int test_convolution() {
    constexpr int nx = 5;
    constexpr int ny = 5;
    std::vector<double> input(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> output(static_cast<size_t>(nx * ny), 0.0);

    auto index = [ny](int ix, int iy) {
        return static_cast<size_t>(ix) * static_cast<size_t>(ny) + static_cast<size_t>(iy);
    };

    // Дельта-источник в центре фотометрической матрицы
    input[index(2, 2)] = 1.0;

    comtails_convolution_cpu(input.data(), output.data(), nx, ny, 2.5);

    double sum = 0.0;
    for (double v : output) {
        if (v < 0.0) {
            std::cerr << "Ошибка: свёртка дала отрицательную яркость\n";
            return 1;
        }
        sum += v;
    }

    if (!(sum > 0.90 && sum <= 1.0)) {
        std::cerr << "Ошибка: свёртка нарушила энергетический баланс, sum=" << sum << "\n";
        return 1;
    }

    const double center = output[index(2, 2)];
    if (!(center >= output[index(2, 1)] && center >= output[index(1, 2)])) {
        std::cerr << "Ошибка: максимум PSF не в центральном пикселе\n";
        return 1;
    }

    return 0;
}

int test_accumulation() {
    constexpr int nx = 4;
    constexpr int ny = 4;
    std::vector<double> flux(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> opt_depth(static_cast<size_t>(nx * ny), 0.0);
    double opt_depth_nuc = 0.0;

    const std::vector<double> npar{0.0, 5.0, 0.0};
    const std::vector<double> mpar{0.0, 5.0, 0.0};
    const std::vector<double> lpar{1.0, 1.0, -1.0};
    const std::vector<double> rad{1e-4, 1e-4, 2e-4};
    const std::vector<double> eneint{2.0, 3.0, 1.0};

    comtails_accumulate_particles_cpu(
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(), npar.size(),
        -10.0, 10.0, -10.0, 10.0, 0.2, 0.2,
        nx, ny, 2, 2, 1.0, 1000.0,
        flux.data(), opt_depth.data(), &opt_depth_nuc);

    auto index = [ny](int ix, int iy) {
        return static_cast<size_t>(ix) * static_cast<size_t>(ny) + static_cast<size_t>(iy);
    };

    if (!approx(flux[index(2, 2)], 2.0 * 1e-8 + 1.0 * 4e-8, 1e-16)) {
        std::cerr << "Ошибка: аккумуляция потока\n";
        return 1;
    }

    if (!(opt_depth[index(2, 2)] > 0.0)) {
        std::cerr << "Ошибка: аккумуляция оптической толщины\n";
        return 1;
    }

    if (!(opt_depth_nuc > 0.0 && opt_depth_nuc < opt_depth[index(2, 2)])) {
        std::cerr << "Ошибка: расчёт центральной оптической толщины ядра\n";
        return 1;
    }

    return 0;
}

int test_velocity_sampler() {
    constexpr size_t count = 16;
    std::vector<double> vx1(count, 0.0), vy1(count, 0.0), vz1(count, 0.0);
    std::vector<double> vx2(count, 0.0), vy2(count, 0.0), vz2(count, 0.0);

    comtails_sample_isotropic_velocity_cpu(120.0, 12345ULL, count, vx1.data(), vy1.data(), vz1.data());
    comtails_sample_isotropic_velocity_cpu(120.0, 12345ULL, count, vx2.data(), vy2.data(), vz2.data());

    const double expected_norm = 5.775483e-4 * 120.0;
    for (size_t i = 0; i < count; ++i) {
        if (!approx(vx1[i], vx2[i], 1e-14) || !approx(vy1[i], vy2[i], 1e-14) || !approx(vz1[i], vz2[i], 1e-14)) {
            std::cerr << "Ошибка: детерминизм генератора скоростей\n";
            return 1;
        }

        const double norm = std::sqrt(vx1[i] * vx1[i] + vy1[i] * vy1[i] + vz1[i] * vz1[i]);
        if (!approx(norm, expected_norm, 1e-12)) {
            std::cerr << "Ошибка: модуль скорости выброса\n";
            return 1;
        }
    }

    return 0;
}

int test_monte_carlo_step() {
    constexpr size_t count = 8;
    constexpr int nx = 4;
    constexpr int ny = 4;

    std::vector<double> npar(count, 0.0), mpar(count, 0.0), lpar(count, 1.0), rad(count, 1e-4), eneint(count, 1.0);
    std::vector<double> flux(static_cast<size_t>(nx * ny), 0.0), opt_depth(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> vx(count, 0.0), vy(count, 0.0), vz(count, 0.0);
    double opt_depth_nuc = 0.0;

    comtails_monte_carlo_step_cpu(
        120.0, 20260327ULL, count,
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(),
        -10.0, 10.0, -10.0, 10.0, 0.2, 0.2,
        nx, ny, 2, 2, 1.0, 1000.0,
        flux.data(), opt_depth.data(), &opt_depth_nuc,
        vx.data(), vy.data(), vz.data());

    auto index = [ny](int ix, int iy) {
        return static_cast<size_t>(ix) * static_cast<size_t>(ny) + static_cast<size_t>(iy);
    };

    if (!(flux[index(2, 2)] > 0.0 && opt_depth[index(2, 2)] > 0.0 && opt_depth_nuc > 0.0)) {
        std::cerr << "Ошибка: batched Monte Carlo шаг не внёс фотометрический вклад\n";
        return 1;
    }

    for (size_t i = 0; i < count; ++i) {
        const double norm = std::sqrt(vx[i] * vx[i] + vy[i] * vy[i] + vz[i] * vz[i]);
        if (!(norm > 0.0)) {
            std::cerr << "Ошибка: скорости после Monte Carlo шага не рассчитаны\n";
            return 1;
        }
    }

    return 0;
}


int test_monte_carlo_step_v2_scaling() {
    constexpr size_t count = 4;
    constexpr int nx = 4;
    constexpr int ny = 4;

    std::vector<double> npar(count, 0.0), mpar(count, 0.0), lpar(count, 1.0), rad(count, 1e-4), eneint(count, 1.0);
    std::vector<double> flux10(static_cast<size_t>(nx * ny), 0.0), depth10(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> flux20(static_cast<size_t>(nx * ny), 0.0), depth20(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> vx(count, 0.0), vy(count, 0.0), vz(count, 0.0);
    double nuc10 = 0.0;
    double nuc20 = 0.0;

    comtails_monte_carlo_step_v2_cpu(
        120.0, 42ULL, count, 10,
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(),
        -10.0, 10.0, -10.0, 10.0, 0.2, 0.2,
        nx, ny, 2, 2, 1.0, 1000.0,
        flux10.data(), depth10.data(), &nuc10,
        vx.data(), vy.data(), vz.data());

    comtails_monte_carlo_step_v2_cpu(
        120.0, 42ULL, count, 20,
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(),
        -10.0, 10.0, -10.0, 10.0, 0.2, 0.2,
        nx, ny, 2, 2, 1.0, 1000.0,
        flux20.data(), depth20.data(), &nuc20,
        vx.data(), vy.data(), vz.data());

    auto idx = [ny](int ix, int iy) {
        return static_cast<size_t>(ix) * static_cast<size_t>(ny) + static_cast<size_t>(iy);
    };

    const double f10 = flux10[idx(2, 2)];
    const double f20 = flux20[idx(2, 2)];
    if (!(f10 > 0.0 && approx(f20, f10 * 0.5, 1e-18))) {
        std::cerr << "Ошибка: нормировка /nevent в v2 не соблюдена для потока\n";
        return 1;
    }

    const double d10 = depth10[idx(2, 2)];
    const double d20 = depth20[idx(2, 2)];
    if (!(d10 > 0.0 && approx(d20, d10 * 0.5, 1e-24))) {
        std::cerr << "Ошибка: нормировка /nevent в v2 не соблюдена для оптической толщины\n";
        return 1;
    }

    if (!(nuc10 > 0.0 && approx(nuc20, nuc10 * 0.5, 1e-24))) {
        std::cerr << "Ошибка: нормировка /nevent в v2 не соблюдена для ядра\n";
        return 1;
    }

    return 0;
}

}  // namespace

int main() {
    if (test_interp() != 0) return 1;
    if (test_convolution() != 0) return 1;
    if (test_accumulation() != 0) return 1;
    if (test_velocity_sampler() != 0) return 1;
    if (test_monte_carlo_step() != 0) return 1;
    if (test_monte_carlo_step_v2_scaling() != 0) return 1;

    std::cout << "comtails_core_tests: OK\n";
    return 0;
}
