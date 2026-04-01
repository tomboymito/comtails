#include "comtails_core.h"

#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <tuple>
#include <vector>

struct Scenario {
    const char* name;
    size_t count;
    unsigned long long seed;
    int nevent;
};

struct Metrics {
    double elapsed_ms;
    double flux_sum;
    double depth_sum;
    double depth_nuc;
    double vnorm0;
};

Metrics run_scenario(const Scenario& sc) {
    const int nx = 512;
    const int ny = 512;

    std::vector<double> npar(sc.count, 0.0), mpar(sc.count, 0.0), lpar(sc.count, 1.0), rad(sc.count, 1e-4), eneint(sc.count, 1.0);
    std::vector<double> flux(static_cast<size_t>(nx * ny), 0.0), opt_depth(static_cast<size_t>(nx * ny), 0.0);
    std::vector<double> vx(sc.count, 0.0), vy(sc.count, 0.0), vz(sc.count, 0.0);

    std::mt19937_64 rng(sc.seed);
    std::uniform_real_distribution<double> unif(-9.5, 9.5);
    std::uniform_real_distribution<double> urad(5e-6, 2e-4);
    std::uniform_real_distribution<double> uene(0.1, 4.0);

    for (size_t i = 0; i < sc.count; ++i) {
        npar[i] = unif(rng);
        mpar[i] = unif(rng);
        rad[i] = urad(rng);
        eneint[i] = uene(rng);
    }

    double opt_depth_nuc = 0.0;
    auto t0 = std::chrono::high_resolution_clock::now();
    comtails_monte_carlo_step_v2_cpu(
        120.0, sc.seed, sc.count, sc.nevent,
        npar.data(), mpar.data(), lpar.data(), rad.data(), eneint.data(),
        -10.0, 10.0, -10.0, 10.0,
        25.6, 25.6,
        nx, ny, nx / 2, ny / 2,
        1.0, 1000.0,
        flux.data(), opt_depth.data(), &opt_depth_nuc,
        vx.data(), vy.data(), vz.data());
    auto t1 = std::chrono::high_resolution_clock::now();

    double flux_sum = 0.0;
    double depth_sum = 0.0;
    for (size_t i = 0; i < flux.size(); ++i) {
        flux_sum += flux[i];
        depth_sum += opt_depth[i];
    }

    Metrics m{};
    m.elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    m.flux_sum = flux_sum;
    m.depth_sum = depth_sum;
    m.depth_nuc = opt_depth_nuc;
    m.vnorm0 = std::sqrt(vx[0] * vx[0] + vy[0] * vy[0] + vz[0] * vz[0]);
    return m;
}

int main(int argc, char** argv) {
    const std::vector<Scenario> scenarios = {
        {"small", 100000, 20260401ULL, 150},
        {"medium", 300000, 20260402ULL, 150},
        {"large", 600000, 20260403ULL, 150},
    };

    std::ofstream csv;
    bool write_csv = false;
    if (argc > 1) {
        csv.open(argv[1]);
        if (csv.is_open()) {
            write_csv = true;
            csv << "scenario,count,seed,nevent,elapsed_ms,flux_sum,depth_sum,depth_nuc,vnorm0\n";
        }
    }

    std::cout << "=== CPU parity dataset (Monte Carlo) ===\n";
    std::cout << "scenario\tcount\tseed\tnevent\telapsed_ms\tflux_sum\tdepth_sum\tdepth_nuc\tvnorm0\n";

    for (const auto& sc : scenarios) {
        const Metrics m = run_scenario(sc);
        std::cout << sc.name << "\t" << sc.count << "\t" << sc.seed << "\t" << sc.nevent << "\t"
                  << m.elapsed_ms << "\t" << m.flux_sum << "\t" << m.depth_sum << "\t"
                  << m.depth_nuc << "\t" << m.vnorm0 << "\n";

        if (write_csv) {
            csv << sc.name << "," << sc.count << "," << sc.seed << "," << sc.nevent << ","
                << m.elapsed_ms << "," << m.flux_sum << "," << m.depth_sum << ","
                << m.depth_nuc << "," << m.vnorm0 << "\n";
        }
    }

    if (write_csv) {
        std::cout << "CSV сохранён: " << argv[1] << "\n";
    }

    return 0;
}
