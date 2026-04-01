#include "comtails_core.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>

namespace fs = std::filesystem;

static void write_matrix_csv(const std::string& path, const std::vector<double>& a, int nx, int ny) {
    std::ofstream out(path);
    for (int ix = 0; ix < nx; ++ix) {
        for (int iy = 0; iy < ny; ++iy) {
            const size_t id = static_cast<size_t>(ix) * static_cast<size_t>(ny) + static_cast<size_t>(iy);
            out << a[id];
            if (iy + 1 < ny) out << ',';
        }
        out << '\n';
    }
}

int main(int argc, char** argv) {
    const size_t count = (argc > 1) ? static_cast<size_t>(std::stoull(argv[1])) : 200000;
    const int nx = 256;
    const int ny = 256;
    const int nevent = 150;

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
    comtails_monte_carlo_step_v2_cpu(
        120.0, 20260401ULL, count, nevent,
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(),
        -10.0, 10.0, -10.0, 10.0, 12.8, 12.8,
        nx, ny, nx / 2, ny / 2,
        1.0, 1000.0,
        flux.data(), opt_depth.data(), &opt_depth_nuc,
        vx.data(), vy.data(), vz.data());

    fs::create_directories("output_cpp");
    write_matrix_csv("output_cpp/flux.csv", flux, nx, ny);
    write_matrix_csv("output_cpp/opt_depth.csv", opt_depth, nx, ny);

    std::cout << "Синтетический C++ расчёт завершён\n";
    std::cout << "Частиц: " << count << "\n";
    std::cout << "Файлы: output_cpp/flux.csv, output_cpp/opt_depth.csv\n";
    std::cout << "Оптическая толщина ядра: " << opt_depth_nuc << "\n";
    return 0;
}
