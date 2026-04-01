#include "comtails_core.h"

#include <cmath>
#include <random>
#include <stdexcept>
#include <vector>

namespace {

inline comtails_interp_result_t make_result(
    const double* dmdtlog,
    const double* powera,
    const double* velfac,
    const double* radiomin,
    const double* radiomax,
    size_t i) {
    return {dmdtlog[i], powera[i], velfac[i], radiomin[i], radiomax[i]};
}

inline size_t pixel_index(int ix, int iy, int ny) {
    return static_cast<size_t>(ix) * static_cast<size_t>(ny) + static_cast<size_t>(iy);
}

}  // namespace

comtails_interp_result_t comtails_interp5_cpu(
    double xdtime,
    const double* dtime,
    const double* dmdtlog,
    const double* powera,
    const double* velfac,
    const double* radiomin,
    const double* radiomax,
    size_t ninputs) {
    if (ninputs == 0) {
        throw std::invalid_argument("ninputs must be > 0");
    }

    if (xdtime <= dtime[0]) {
        return make_result(dmdtlog, powera, velfac, radiomin, radiomax, 0);
    }
    if (xdtime >= dtime[ninputs - 1]) {
        return make_result(dmdtlog, powera, velfac, radiomin, radiomax, ninputs - 1);
    }

    size_t left = 0;
    size_t right = ninputs - 1;
    while (right - left > 1) {
        const size_t mid = (left + right) / 2;
        if (dtime[mid] > xdtime) {
            right = mid;
        } else {
            left = mid;
        }
    }

    const size_t i = right;
    const double delta = dtime[i] - dtime[i - 1];
    const double factor = (xdtime - dtime[i - 1]) / delta;

    comtails_interp_result_t result{};
    result.dmdtl = dmdtlog[i - 1] + factor * (dmdtlog[i] - dmdtlog[i - 1]);
    result.vfac = velfac[i - 1] + factor * (velfac[i] - velfac[i - 1]);
    result.power = powera[i - 1] + factor * (powera[i] - powera[i - 1]);
    result.radmin = radiomin[i - 1] + factor * (radiomin[i] - radiomin[i - 1]);
    result.radmax = radiomax[i - 1] + factor * (radiomax[i] - radiomax[i - 1]);
    return result;
}

void comtails_convolution_cpu(const double* input, double* output, int nx, int ny, double sfwhm) {
    if (nx <= 0 || ny <= 0) {
        return;
    }

    const double sigma = sfwhm / 2.35482;
    const double s2 = sigma * sigma;
    const double ts = 10.0 * sigma;
    const int its = static_cast<int>(ts);
    const int w = its + ((its % 2 == 0) ? 1 : 0);
    const int wbar = (w - 1) / 2;

    std::vector<double> kernel(static_cast<size_t>(w), 0.0);
    double sum = 0.0;
    for (int i = 0; i < w; ++i) {
        const double x = static_cast<double>(i - wbar);
        kernel[static_cast<size_t>(i)] = std::exp(-x * x / (2.0 * s2));
        sum += kernel[static_cast<size_t>(i)];
    }
    for (double& k : kernel) {
        k /= sum;
    }

    const size_t total = static_cast<size_t>(nx) * static_cast<size_t>(ny);
    std::vector<double> aux(total, 0.0);

    // Свёртка по оси X
    for (int iy = 0; iy < ny; ++iy) {
        for (int ix = 0; ix < nx; ++ix) {
            double val = 0.0;
            for (int i = 0; i < w; ++i) {
                const int xx = ix - wbar + i;
                if (xx >= 0 && xx < nx) {
                    val += kernel[static_cast<size_t>(i)] * input[pixel_index(xx, iy, ny)];
                }
            }
            aux[pixel_index(ix, iy, ny)] = val;
        }
    }

    // Свёртка по оси Y
    for (int iy = 0; iy < ny; ++iy) {
        for (int ix = 0; ix < nx; ++ix) {
            double val = 0.0;
            for (int i = 0; i < w; ++i) {
                const int yy = iy - wbar + i;
                if (yy >= 0 && yy < ny) {
                    val += kernel[static_cast<size_t>(i)] * aux[pixel_index(ix, yy, ny)];
                }
            }
            output[pixel_index(ix, iy, ny)] = val;
        }
    }

    (void)total;
}

void comtails_accumulate_particles_cpu(
    const double* npar,
    const double* mpar,
    const double* lpar,
    const double* rad,
    const double* eneint,
    size_t count,
    double nmin,
    double nmax,
    double mmin,
    double mmax,
    double augx,
    double augy,
    int nx,
    int ny,
    int inuc,
    int jnuc,
    double cte_part,
    double grdsiz,
    double* flux,
    double* opt_depth,
    double* opt_depth_nuc) {
    if (nx <= 0 || ny <= 0 || flux == nullptr || opt_depth == nullptr || opt_depth_nuc == nullptr) {
        return;
    }

    for (size_t i = 0; i < count; ++i) {
        const double np = npar[i];
        const double mp = mpar[i];

        if (np < nmin || np > nmax || mp < mmin || mp > mmax) {
            continue;
        }

        const int ii = static_cast<int>((np - nmin) * augx);
        const int jj = static_cast<int>((mp - mmin) * augy);
        if (ii < 0 || ii >= nx || jj < 0 || jj >= ny) {
            continue;
        }

        const double flux_out = cte_part * rad[i] * rad[i];
        const double particle_contribution = flux_out * eneint[i];
        flux[pixel_index(ii, jj, ny)] += particle_contribution;

        const double depth_contribution =
            2.0 * eneint[i] * M_PI * std::pow(rad[i] / (grdsiz * 1.0e3), 2.0);
        opt_depth[pixel_index(ii, jj, ny)] += depth_contribution;

        if (lpar[i] > 0.0 && ii == inuc && jj == jnuc) {
            *opt_depth_nuc += depth_contribution;
        }
    }
}

void comtails_sample_isotropic_velocity_cpu(
    double vej,
    unsigned long long seed,
    size_t count,
    double* vx,
    double* vy,
    double* vz) {
    if (vx == nullptr || vy == nullptr || vz == nullptr || count == 0) {
        return;
    }

    constexpr double kCteVel = 5.775483e-4;  // км/с -> а.е./сут
    const double speed = kCteVel * vej;

    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> uni01(0.0, 1.0);

    for (size_t i = 0; i < count; ++i) {
        const double random1 = uni01(rng);
        const double random2 = uni01(rng);
        const double phi = 2.0 * M_PI * random1;
        const double theta = std::acos(2.0 * random2 - 1.0);

        const double sx = std::sin(theta) * std::cos(phi);
        const double sy = std::sin(theta) * std::sin(phi);
        const double sz = std::cos(theta);

        vx[i] = speed * sx;
        vy[i] = speed * sy;
        vz[i] = speed * sz;
    }
}

void comtails_monte_carlo_step_cpu(
    double vej,
    unsigned long long seed,
    size_t count,
    const double* npar,
    const double* mpar,
    const double* lpar,
    const double* rad,
    const double* eneint,
    double nmin,
    double nmax,
    double mmin,
    double mmax,
    double augx,
    double augy,
    int nx,
    int ny,
    int inuc,
    int jnuc,
    double cte_part,
    double grdsiz,
    double* flux,
    double* opt_depth,
    double* opt_depth_nuc,
    double* vx,
    double* vy,
    double* vz) {
    comtails_sample_isotropic_velocity_cpu(vej, seed, count, vx, vy, vz);

    comtails_accumulate_particles_cpu(
        npar, mpar, lpar, rad, eneint, count,
        nmin, nmax, mmin, mmax, augx, augy,
        nx, ny, inuc, jnuc, cte_part, grdsiz,
        flux, opt_depth, opt_depth_nuc);
}

void comtails_monte_carlo_step_v2_cpu(
    double vej,
    unsigned long long seed,
    size_t count,
    int nevent,
    const double* npar,
    const double* mpar,
    const double* lpar,
    const double* rad,
    const double* eneint,
    double nmin,
    double nmax,
    double mmin,
    double mmax,
    double augx,
    double augy,
    int nx,
    int ny,
    int inuc,
    int jnuc,
    double cte_part,
    double grdsiz,
    double* flux,
    double* opt_depth,
    double* opt_depth_nuc,
    double* vx,
    double* vy,
    double* vz) {
    comtails_sample_isotropic_velocity_cpu(vej, seed, count, vx, vy, vz);

    if (nevent <= 0 || nx <= 0 || ny <= 0 || flux == nullptr || opt_depth == nullptr || opt_depth_nuc == nullptr) {
        return;
    }

    const double inv_nevent = 1.0 / static_cast<double>(nevent);

    for (size_t i = 0; i < count; ++i) {
        const double np = npar[i];
        const double mp = mpar[i];
        if (np < nmin || np > nmax || mp < mmin || mp > mmax) {
            continue;
        }

        const int ii = static_cast<int>((np - nmin) * augx);
        const int jj = static_cast<int>((mp - mmin) * augy);
        if (ii < 0 || ii >= nx || jj < 0 || jj >= ny) {
            continue;
        }

        const double flux_out = cte_part * rad[i] * rad[i];
        const double particle_contribution = flux_out * eneint[i] * inv_nevent;
        flux[pixel_index(ii, jj, ny)] += particle_contribution;

        const double depth_contribution =
            2.0 * eneint[i] * M_PI * std::pow(rad[i] / (grdsiz * 1.0e3), 2.0) * inv_nevent;
        opt_depth[pixel_index(ii, jj, ny)] += depth_contribution;

        if (lpar[i] > 0.0 && ii == inuc && jj == jnuc) {
            *opt_depth_nuc += depth_contribution;
        }
    }
}
