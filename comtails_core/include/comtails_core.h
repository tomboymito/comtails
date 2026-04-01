#ifndef COMTAILS_CORE_H
#define COMTAILS_CORE_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double dmdtl;
    double power;
    double vfac;
    double radmin;
    double radmax;
} comtails_interp_result_t;

/**
 * CPU-референс интерполяции профиля пылепроизводства.
 * Повторяет логику DustTail._interp5.
 */
comtails_interp_result_t comtails_interp5_cpu(
    double xdtime,
    const double* dtime,
    const double* dmdtlog,
    const double* powera,
    const double* velfac,
    const double* radiomin,
    const double* radiomax,
    size_t ninputs);

/**
 * CPU-референс сепарабельной гауссовой свёртки (по X, затем по Y).
 * Массивы вход/выход имеют row-major раскладку [nx, ny].
 */
void comtails_convolution_cpu(
    const double* input,
    double* output,
    int nx,
    int ny,
    double sfwhm);

/**
 * CPU-референс ядра аккумуляции частиц в фотометрической матрице.
 *
 * Для каждой частицы вычисляет индексы пикселя и накапливает поток
 * и оптическую толщину по тем же формулам, что и Python-реализация.
 */
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
    double* opt_depth_nuc);

/**
 * Детерминированный изотропный отбор скоростей выброса (режим 1).
 *
 * Генерирует направления на единичной сфере и масштабирует их на CTEVEL * vej.
 * Выходные массивы должны иметь длину `count`.
 */
void comtails_sample_isotropic_velocity_cpu(
    double vej,
    unsigned long long seed,
    size_t count,
    double* vx,
    double* vy,
    double* vz);

/**
 * Шаг батчевого Monte Carlo (CPU):
 * 1) детерминированный изотропный отбор скоростей,
 * 2) аккумуляция фотометрического вклада частиц в карту потока и оптической толщины.
 *
 * Массивы `lpar` и `eneint` должны иметь длину `count`.
 */
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
    double* vz);


/**
 * Шаг batched Monte Carlo (v2) с явной нормировкой на число событий выброса.
 *
 * Вклад каждой частицы масштабируется как в Python-контуре: / nevent.
 */
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
    double* vz);

#ifdef __cplusplus
}
#endif

#endif
