#include "comtails_core.h"

#include <chrono>
#include <cmath>
#include <iostream>
#include <random>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    const size_t count = (argc > 1) ? static_cast<size_t>(std::stoull(argv[1])) : 200000;
    const int nx = 512;
    const int ny = 512;

    std::vector<double> npar(count, 0.0), mpar(count, 0.0), lpar(count, 1.0), rad(count, 1e-4), eneint(count, 1.0);
    std::vector<double> flux(static_cast<size_t>(nx * ny), 0.0), opt_depth(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> vx(count, 0.0), vy(count, 0.0), vz(count, 0.0);

    std::mt19937_64 rng(20260401ULL);
    std::uniform_real_distribution<double> unif(-9.5, 9.5);
    std::uniform_real_distribution<double> urad(5e-6, 2e-4);
    std::uniform_real_distribution<double> uene(0.1, 4.0);

    for (size_t i = 0; i < count; ++i) {
        npar[i] = unif(rng);
        mpar[i] = unif(rng);
        rad[i] = urad(rng);
        eneint[i] = uene(rng);
    }

    double opt_depth_nuc = 0.0;

    auto t0 = std::chrono::high_resolution_clock::now();
    comtails_monte_carlo_step_cpu(
        120.0, 20260401ULL, count,
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(),
        -10.0, 10.0, -10.0, 10.0,
        25.6, 25.6,
        nx, ny, nx / 2, ny / 2,
        1.0, 1000.0,
        flux.data(), opt_depth.data(), &opt_depth_nuc,
        vx.data(), vy.data(), vz.data());
    auto t1 = std::chrono::high_resolution_clock::now();

    const double elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    double sum_flux = 0.0;
    double sum_depth = 0.0;
    for (size_t i = 0; i < flux.size(); ++i) {
        sum_flux += flux[i];
        sum_depth += opt_depth[i];
    }

    std::cout << "=== Бенчмарк batched Monte Carlo (CPU) ===\n";
    std::cout << "Частиц: " << count << "\n";
    std::cout << "Размер матрицы: " << nx << "x" << ny << "\n";
    std::cout << "Время шага: " << elapsed_ms << " мс\n";
    std::cout << "Суммарный фотометрический поток: " << sum_flux << "\n";
    std::cout << "Суммарная оптическая толщина: " << sum_depth << "\n";
    std::cout << "Оптическая толщина вблизи ядра: " << opt_depth_nuc << "\n";

    // Контроль не-нулевых скоростей
    double vnorm0 = std::sqrt(vx[0] * vx[0] + vy[0] * vy[0] + vz[0] * vz[0]);
    std::cout << "Модуль первой скорости выброса: " << vnorm0 << "\n";

    return 0;
}
