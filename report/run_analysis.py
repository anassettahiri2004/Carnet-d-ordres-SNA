"""
Reproduit (et complete) toutes les analyses du notebook carnet_d_ordres.ipynb.

Sauvegarde :
- les figures necessaires au rapport dans report/figures/*.png
- un fichier results.json avec tous les chiffres a citer dans le .tex
"""

import json
import os
import time
import numpy as np
import scipy.stats as sps
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

np.random.seed(42)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(OUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Parametres globaux (identiques au notebook)
# ---------------------------------------------------------------------------
LAMBDA_PLUS = 1.2
LAMBDA_MINUS = 2.0
T = 100
Q_0 = 10
Q_0_A = 10
Q_0_B = 10
Q_0_2 = 10
LAMBDA_PLUS_2 = 1.2
LAMBDA_MINUS_2 = 2.0


# ---------------------------------------------------------------------------
# Simulateurs (copies depuis le notebook)
# ---------------------------------------------------------------------------
def simulate_only_one_process(lambda_plus, lambda_minus, q_0=Q_0_A,
                              stopping_condition=lambda q, t: q > 0):
    q = q_0
    times = [0.0]
    q_values = [q]
    while stopping_condition(q, times[-1]):
        total_rate = lambda_plus + lambda_minus
        dt = np.random.exponential(1.0 / total_rate)
        times.append(times[-1] + dt)
        if np.random.rand() < lambda_plus / total_rate:
            q += 1
        else:
            q -= 1
        q_values.append(max(0, q))
    return times, q_values


def simulate_poisson_process_until_zero(lambda_plus, lambda_minus,
                                        q_0_a=Q_0_A, q_0_b=Q_0_B):
    times_b, q_b = simulate_only_one_process(lambda_plus, lambda_minus, q_0_b)
    times_a, q_a = simulate_only_one_process(lambda_plus, lambda_minus, q_0_a)
    return times_b, q_b, times_a, q_a


def estimate_time_to_zero(lambda_plus, lambda_minus, q_0_a=Q_0_A, q_0_b=Q_0_B,
                          num_simulations=1000, quantile=0.95):
    samples = np.empty(num_simulations)
    for i in range(num_simulations):
        tb, _, ta, _ = simulate_poisson_process_until_zero(
            lambda_plus, lambda_minus, q_0_a, q_0_b)
        samples[i] = min(tb[-1], ta[-1])
    m = samples.mean()
    se = samples.std(ddof=1) / np.sqrt(num_simulations)
    z = sps.norm.ppf((1 + quantile) / 2)
    return m, m - z * se, m + z * se


def estimate_time_to_zero_for_one_process(lambda_plus, lambda_minus, q_0=Q_0_A,
                                          num_simulations=1000, quantile=0.95):
    samples = np.empty(num_simulations)
    for i in range(num_simulations):
        t, _ = simulate_only_one_process(lambda_plus, lambda_minus, q_0)
        samples[i] = t[-1]
    m = samples.mean()
    se = samples.std(ddof=1) / np.sqrt(num_simulations)
    z = sps.norm.ppf((1 + quantile) / 2)
    return m, m - z * se, m + z * se


def determine_lambda_minus_stationarity(mu_minus, alpha, beta, lambda_plus=LAMBDA_PLUS):
    return (mu_minus * beta - lambda_plus * alpha) / (beta - alpha)


def hawkes_simulation(mu_minus, alpha, beta, lambda_plus=LAMBDA_PLUS, q_0=Q_0,
                      stopping_condition=lambda q, t: t > T):
    q = q_0
    t = 0.0
    t_last = 0.0
    lambda_minus_t = mu_minus
    times = [t]
    q_values = [q]
    lambda_minus_list = [lambda_minus_t]
    while not stopping_condition(q, t):
        lambda_bar = max(mu_minus, lambda_minus_t)
        sup_lambda = lambda_bar + lambda_plus
        dt = np.random.exponential(1.0 / sup_lambda)
        t_prime = t + dt
        lambda_pre = mu_minus + (lambda_minus_t - mu_minus) * np.exp(-beta * (t_prime - t_last))
        lambda_eff = max(lambda_pre, 0.0)
        U = np.random.rand()
        if U < lambda_plus / sup_lambda:
            q += 1
            t = t_prime
            t_last = t
            lambda_minus_t = lambda_pre - alpha
            times.append(t); q_values.append(q); lambda_minus_list.append(lambda_minus_t)
        elif U < (lambda_eff + lambda_plus) / sup_lambda:
            q -= 1
            t = t_prime
            t_last = t
            lambda_minus_t = lambda_pre + alpha
            times.append(t); q_values.append(q); lambda_minus_list.append(lambda_minus_t)
        else:
            lambda_minus_t = lambda_pre
            t_last = t_prime
            t = t_prime
    return times, q_values, lambda_minus_list


def simulated_coupled_hawkes_processes(mu_minus_a, mu_minus_b, alpha, beta,
                                       lambda_plus_a=LAMBDA_PLUS, lambda_plus_b=LAMBDA_PLUS,
                                       q_0_a=Q_0_A, q_0_b=Q_0_B):
    q_a = q_0_a; q_b = q_0_b; t = 0.0
    t_last_a = 0.0; t_last_b = 0.0
    lambda_minus_a_t = mu_minus_a; lambda_minus_b_t = mu_minus_b
    times = [t]; times_a = [t]; times_b = [t]
    q_a_values = [q_a]; q_b_values = [q_b]
    while q_a > 0 and q_b > 0:
        lambda_bar_a = max(mu_minus_a, lambda_minus_a_t)
        lambda_bar_b = max(mu_minus_b, lambda_minus_b_t)
        sup_lambda = lambda_bar_a + lambda_bar_b + lambda_plus_a + lambda_plus_b
        dt = np.random.exponential(1.0 / sup_lambda)
        t_prime = t + dt
        lambda_pre_a = mu_minus_a + (lambda_minus_a_t - mu_minus_a) * np.exp(-beta * (t_prime - t_last_a))
        lambda_pre_b = mu_minus_b + (lambda_minus_b_t - mu_minus_b) * np.exp(-beta * (t_prime - t_last_b))
        lambda_eff_a = max(lambda_pre_a, 0.0)
        lambda_eff_b = max(lambda_pre_b, 0.0)
        U = np.random.rand()
        if U < lambda_plus_a / sup_lambda:
            q_a += 1; t = t_prime; t_last_a = t
            lambda_minus_a_t = lambda_pre_a - alpha
            lambda_minus_b_t = lambda_pre_b + alpha
            times.append(t); times_a.append(t); q_a_values.append(q_a)
        elif U < (lambda_eff_a + lambda_plus_a) / sup_lambda:
            q_a -= 1; t = t_prime; t_last_a = t
            lambda_minus_a_t = lambda_pre_a + alpha
            lambda_minus_b_t = lambda_pre_b - alpha
            times.append(t); times_a.append(t); q_a_values.append(q_a)
        elif U < (lambda_bar_a + lambda_plus_a) / sup_lambda:
            lambda_minus_a_t = lambda_pre_a
            lambda_minus_b_t = lambda_pre_b
            t_last_a = t_prime; t = t_prime
        elif U < (lambda_bar_a + lambda_plus_a + lambda_plus_b) / sup_lambda:
            q_b += 1; t = t_prime; t_last_b = t
            lambda_minus_b_t = lambda_pre_b - alpha
            lambda_minus_a_t = lambda_pre_a + alpha
            times.append(t); times_b.append(t); q_b_values.append(q_b)
        elif U < (lambda_bar_a + lambda_plus_a + lambda_eff_b + lambda_plus_b) / sup_lambda:
            q_b -= 1; t = t_prime; t_last_b = t
            lambda_minus_b_t = lambda_pre_b + alpha
            lambda_minus_a_t = lambda_pre_a - alpha
            times.append(t); times_b.append(t); q_b_values.append(q_b)
        else:
            lambda_minus_b_t = lambda_pre_b
            lambda_minus_a_t = lambda_pre_a
            t_last_b = t_prime; t = t_prime
    return times, times_a, times_b, q_a_values, q_b_values


def probability_ask_first(lambda_plus, lambda_minus, q_0_a, q_0_b, num_simulations=1000):
    cnt = 0
    for _ in range(num_simulations):
        tb, _, ta, _ = simulate_poisson_process_until_zero(
            lambda_plus, lambda_minus, q_0_a, q_0_b)
        if ta[-1] < tb[-1]:
            cnt += 1
    return cnt / num_simulations


# ===========================================================================
# 1) Resultats numeriques de base : E[tau] avec IC
# ===========================================================================
results = {}

print("[1] Estimation E[min(tau_a, tau_b)] et E[tau] (un processus)")
m1, lo1, hi1 = estimate_time_to_zero(LAMBDA_PLUS, LAMBDA_MINUS, num_simulations=2000)
m2, lo2, hi2 = estimate_time_to_zero_for_one_process(LAMBDA_PLUS, LAMBDA_MINUS,
                                                      num_simulations=2000)
results["E_min_tau"] = {"mean": m1, "ci_low": lo1, "ci_high": hi1,
                        "theoretical_one_proc": Q_0_A / abs(LAMBDA_PLUS - LAMBDA_MINUS)}
results["E_tau_one"] = {"mean": m2, "ci_low": lo2, "ci_high": hi2,
                        "theoretical": Q_0_A / abs(LAMBDA_PLUS - LAMBDA_MINUS)}
print(f"   E[min(tau_a, tau_b)] = {m1:.3f}  IC95 = [{lo1:.3f}, {hi1:.3f}]")
print(f"   E[tau]               = {m2:.3f}  IC95 = [{lo2:.3f}, {hi2:.3f}]")
print(f"   Reference brownienne E[tau]_th = q_0/|mu| = {Q_0_A / abs(LAMBDA_PLUS - LAMBDA_MINUS):.3f}")


# ===========================================================================
# 2) Validation IG (KS + moments)
# ===========================================================================
print("[2] Validation loi inverse-gaussienne (KS + moments)")
N_ig = 5000
samples = np.empty(N_ig)
for i in range(N_ig):
    times, _ = simulate_only_one_process(LAMBDA_PLUS, LAMBDA_MINUS, Q_0_A)
    samples[i] = times[-1]

drift = LAMBDA_PLUS - LAMBDA_MINUS
sigma2 = LAMBDA_PLUS + LAMBDA_MINUS
mean_th = Q_0_A / abs(drift)
var_th = Q_0_A * sigma2 / abs(drift) ** 3
mu_sc = sigma2 / (Q_0_A * abs(drift))
shape = Q_0_A ** 2 / sigma2
ks_stat, ks_pval = sps.kstest(samples, lambda x: sps.invgauss.cdf(x, mu=mu_sc, scale=shape))
results["IG_validation"] = {
    "N": N_ig,
    "mean_th": mean_th, "mean_emp": float(samples.mean()),
    "var_th": var_th, "var_emp": float(samples.var(ddof=1)),
    "ks_stat": float(ks_stat), "ks_pval": float(ks_pval),
}
print(f"   moyenne th={mean_th:.3f}, emp={samples.mean():.3f}")
print(f"   variance th={var_th:.3f}, emp={samples.var(ddof=1):.3f}")
print(f"   KS : stat={ks_stat:.4f}, p-value={ks_pval:.4f}")

# Figure: histogramme + densite IG
fig, ax = plt.subplots(figsize=(8, 5))
xx = np.linspace(0.01, samples.max(), 400)
ax.hist(samples, bins=80, density=True, alpha=0.55, color="steelblue", label="Simulation Poisson")
ax.plot(xx, sps.invgauss.pdf(xx, mu=mu_sc, scale=shape), "r-", lw=2,
        label=f"Loi IG théorique (KS p={ks_pval:.3f})")
ax.set_xlabel(r"Temps d'atteinte $\tau$"); ax.set_ylabel("Densité")
ax.set_title(r"Adéquation $\tau$ vs loi inverse-gaussienne"
             rf" ($q_0={Q_0_A},\ \lambda^+={LAMBDA_PLUS},\ \lambda^-={LAMBDA_MINUS}$)")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "ig_validation.png"), dpi=130)
plt.close(fig)


# ===========================================================================
# 3) Validation surface MC vs prediction brownienne
# ===========================================================================
print("[3] Validation surface gambler's ruin (MC vs prediction brownienne)")
q_max = 10
surface_mc = np.zeros((q_max, q_max))
surface_th = np.zeros((q_max, q_max))
mean_time_mc = np.zeros((q_max, q_max))
mean_time_lo = np.zeros((q_max, q_max))
mean_time_hi = np.zeros((q_max, q_max))

for i, qa in enumerate(range(1, q_max + 1)):
    for j, qb in enumerate(range(1, q_max + 1)):
        N = 500
        ask_first = 0
        times_min = np.empty(N)
        for k in range(N):
            tb, _, ta, _ = simulate_poisson_process_until_zero(
                LAMBDA_PLUS, LAMBDA_MINUS, q_0_a=qa, q_0_b=qb)
            times_min[k] = min(tb[-1], ta[-1])
            if ta[-1] < tb[-1]:
                ask_first += 1
        surface_mc[j, i] = ask_first / N
        m = times_min.mean()
        se = times_min.std(ddof=1) / np.sqrt(N)
        z = sps.norm.ppf(0.975)
        mean_time_mc[j, i] = m
        mean_time_lo[j, i] = m - z * se
        mean_time_hi[j, i] = m + z * se

        mu_a = sigma2 / (qa * abs(drift)); shape_a = qa ** 2 / sigma2
        mu_b = sigma2 / (qb * abs(drift)); shape_b = qb ** 2 / sigma2
        t_grid = np.linspace(1e-3, 30 * max(qa, qb) / abs(drift), 5000)
        f_a = sps.invgauss.pdf(t_grid, mu=mu_a, scale=shape_a)
        S_b = 1 - sps.invgauss.cdf(t_grid, mu=mu_b, scale=shape_b)
        surface_th[j, i] = float(np.trapezoid(f_a * S_b, t_grid))

err = surface_mc - surface_th
results["proba_surface_validation"] = {
    "max_abs_err": float(np.abs(err).max()),
    "mean_abs_err": float(np.abs(err).mean()),
    "diag_mean": float(np.mean([surface_mc[i, i] for i in range(q_max)])),
}
print(f"   |MC - theorique|_max = {np.abs(err).max():.4f}")
print(f"   |MC - theorique|_moy = {np.abs(err).mean():.4f}")
print(f"   surface_mc sur la diagonale (q_0_a=q_0_b) ~ 0.5 ? moy = {results['proba_surface_validation']['diag_mean']:.4f}")

Q0_A, Q0_B = np.meshgrid(range(1, q_max + 1), range(1, q_max + 1))
fig = plt.figure(figsize=(15, 5))
ax1 = fig.add_subplot(1, 3, 1, projection="3d")
ax1.plot_surface(Q0_A, Q0_B, surface_mc, cmap="viridis", alpha=0.85)
ax1.set_title("Monte-Carlo"); ax1.set_xlabel("$q_0^a$"); ax1.set_ylabel("$q_0^b$"); ax1.set_zlabel("$P$")
ax2 = fig.add_subplot(1, 3, 2, projection="3d")
ax2.plot_surface(Q0_A, Q0_B, surface_th, cmap="viridis", alpha=0.85)
ax2.set_title("Approximation brownienne"); ax2.set_xlabel("$q_0^a$"); ax2.set_ylabel("$q_0^b$"); ax2.set_zlabel("$P$")
ax3 = fig.add_subplot(1, 3, 3, projection="3d")
ax3.plot_surface(Q0_A, Q0_B, err, cmap="coolwarm", alpha=0.85)
ax3.set_title("Erreur (MC - théorique)"); ax3.set_xlabel("$q_0^a$"); ax3.set_ylabel("$q_0^b$"); ax3.set_zlabel("$\\Delta$")
fig.suptitle(r"Surface 3D de $P(\tau_a < \tau_b)$ : MC vs prediction brownienne")
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "ruin_validation.png"), dpi=130)
plt.close(fig)


# Figure : surfaces 3D Poisson independants (E[min] + IC + P)
fig = plt.figure(figsize=(15, 6))
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
surf = ax1.plot_surface(Q0_A, Q0_B, mean_time_mc, cmap="viridis", alpha=0.85)
ax1.plot_wireframe(Q0_A, Q0_B, mean_time_lo, color="red", alpha=0.35, linewidth=0.5)
ax1.plot_wireframe(Q0_A, Q0_B, mean_time_hi, color="black", alpha=0.35, linewidth=0.5)
ax1.set_xlabel("$q_0^a$"); ax1.set_ylabel("$q_0^b$"); ax1.set_zlabel(r"$E[\min(\tau_a,\tau_b)]$")
ax1.set_title("Temps moyen d'épuisement — Poisson")
fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=10)
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
surf2 = ax2.plot_surface(Q0_A, Q0_B, surface_mc, cmap="plasma", alpha=0.85)
ax2.set_xlabel("$q_0^a$"); ax2.set_ylabel("$q_0^b$"); ax2.set_zlabel(r"$P(\tau_a<\tau_b)$")
ax2.set_title("Probabilité ask → 0 en premier — Poisson")
fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "poisson_3d.png"), dpi=130)
plt.close(fig)

results["mean_time_poisson_diag"] = [float(mean_time_mc[i, i]) for i in range(q_max)]
results["mean_time_poisson_corner"] = float(mean_time_mc[-1, -1])


# ===========================================================================
# 4) Validation lambda^- stationnaire (Hawkes)
# ===========================================================================
print("[4] Validation lambda^- stationnaire")
mu_minus, alpha, beta = 2.0, 0.5, 1.0
theoretical_lambda = determine_lambda_minus_stationarity(mu_minus, alpha, beta, LAMBDA_PLUS)

T_long = 2000.0
burn_in = 200.0
N_traj = 100
empirical_means = []
for _ in range(N_traj):
    times, _, lambda_list = hawkes_simulation(
        mu_minus, alpha, beta, LAMBDA_PLUS, q_0=10**6,
        stopping_condition=lambda q, t: t > T_long)
    times_arr = np.asarray(times)
    lam_arr = np.asarray(lambda_list)
    mask = times_arr >= burn_in
    if mask.sum() < 2:
        continue
    t_kept = times_arr[mask]
    lam_kept = lam_arr[mask]
    dt = np.diff(t_kept)
    time_avg = np.sum(lam_kept[:-1] * dt) / (t_kept[-1] - t_kept[0])
    empirical_means.append(time_avg)

empirical_means = np.array(empirical_means)
results["lambda_stationary"] = {
    "theoretical": float(theoretical_lambda),
    "empirical_mean": float(empirical_means.mean()),
    "empirical_std": float(empirical_means.std(ddof=1)),
    "n_traj": len(empirical_means),
    "T_long": T_long,
    "burn_in": burn_in,
    "rel_err_pct": float(100 * (empirical_means.mean() - theoretical_lambda) / theoretical_lambda),
}
print(f"   th = {theoretical_lambda:.3f}")
print(f"   emp = {empirical_means.mean():.3f} +/- {1.96*empirical_means.std(ddof=1)/np.sqrt(len(empirical_means)):.3f}")
print(f"   ecart relatif = {results['lambda_stationary']['rel_err_pct']:+.2f} %")


# ===========================================================================
# 5) Surfaces 3D Hawkes couple (cellule jamais executee dans le notebook)
# ===========================================================================
print("[5] Surfaces 3D Hawkes couple : E[min(tau_a,tau_b)] + P(tau_a<tau_b)")
mu_minus_a = 2.0; mu_minus_b = 2.0
alpha_h = 0.5; beta_h = 1.0
N_cf = 100  # par grain (compromis temps de calcul)
mean_h = np.zeros((q_max, q_max))
lo_h = np.zeros((q_max, q_max))
hi_h = np.zeros((q_max, q_max))
proba_h = np.zeros((q_max, q_max))

t0 = time.time()
for i, qa in enumerate(range(1, q_max + 1)):
    for j, qb in enumerate(range(1, q_max + 1)):
        samples = np.empty(N_cf)
        ask_first = 0
        for k in range(N_cf):
            times, _, _, q_a_values, q_b_values = simulated_coupled_hawkes_processes(
                mu_minus_a, mu_minus_b, alpha_h, beta_h,
                lambda_plus_a=LAMBDA_PLUS, lambda_plus_b=LAMBDA_PLUS,
                q_0_a=qa, q_0_b=qb)
            samples[k] = times[-1]
            if q_a_values[-1] == 0:
                ask_first += 1
        m = samples.mean()
        se = samples.std(ddof=1) / np.sqrt(N_cf)
        z = sps.norm.ppf(0.975)
        mean_h[j, i] = m
        lo_h[j, i] = m - z * se
        hi_h[j, i] = m + z * se
        proba_h[j, i] = ask_first / N_cf
print(f"   surfaces Hawkes couple en {time.time()-t0:.1f}s")

fig = plt.figure(figsize=(15, 6))
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
surf = ax1.plot_surface(Q0_A, Q0_B, mean_h, cmap="viridis", alpha=0.85)
ax1.plot_wireframe(Q0_A, Q0_B, lo_h, color="red", alpha=0.35, linewidth=0.5)
ax1.plot_wireframe(Q0_A, Q0_B, hi_h, color="black", alpha=0.35, linewidth=0.5)
ax1.set_xlabel("$q_0^a$"); ax1.set_ylabel("$q_0^b$"); ax1.set_zlabel(r"$E[\min(\tau_a,\tau_b)]$")
ax1.set_title("Hawkes couplé — temps moyen d'épuisement")
fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=10)
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
surf2 = ax2.plot_surface(Q0_A, Q0_B, proba_h, cmap="plasma", alpha=0.85)
ax2.set_xlabel("$q_0^a$"); ax2.set_ylabel("$q_0^b$"); ax2.set_zlabel(r"$P(\tau_a<\tau_b)$")
ax2.set_title("Hawkes couplé — probabilité ask → 0 en premier")
fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "hawkes_coupled_3d.png"), dpi=130)
plt.close(fig)

results["hawkes_coupled_3d"] = {
    "mean_diag": [float(mean_h[i, i]) for i in range(q_max)],
    "mean_corner": float(mean_h[-1, -1]),
    "proba_diag_mean": float(np.mean([proba_h[i, i] for i in range(q_max)])),
    "ratio_hawkes_to_poisson_corner": float(mean_h[-1, -1] / mean_time_mc[-1, -1]),
}
print(f"   E[min] (Hawkes couple, q0=10) = {mean_h[-1, -1]:.3f}")
print(f"   E[min] (Poisson, q0=10)       = {mean_time_mc[-1, -1]:.3f}")
print(f"   ratio Hawkes/Poisson           = {results['hawkes_coupled_3d']['ratio_hawkes_to_poisson_corner']:.3f}")
print(f"   P(ask first) sur diag           = {results['hawkes_coupled_3d']['proba_diag_mean']:.4f}")


# ===========================================================================
# 6) Comparaison directe distributions de temps d'arret 4 modeles
# ===========================================================================
print("[6] Comparaison 4 modeles : moyennes et quantiles du temps d'arret")
N_cmp = 1000

samp_poisson = np.array([simulate_only_one_process(LAMBDA_PLUS, LAMBDA_MINUS, Q_0)[0][-1]
                         for _ in range(N_cmp)])
samp_first2 = np.array([min(simulate_poisson_process_until_zero(LAMBDA_PLUS, LAMBDA_MINUS,
                                                                Q_0, Q_0)[0][-1],
                            simulate_poisson_process_until_zero(LAMBDA_PLUS, LAMBDA_MINUS,
                                                                Q_0, Q_0)[2][-1])
                       for _ in range(N_cmp)])

# Hawkes simple
samp_hawkes = []
for _ in range(N_cmp):
    times, _, _ = hawkes_simulation(2.0, 0.5, 1.0, LAMBDA_PLUS, q_0=Q_0,
                                    stopping_condition=lambda q, t: q == 0)
    samp_hawkes.append(times[-1])
samp_hawkes = np.array(samp_hawkes)

# Hawkes couple (plus court - 200 simulations seulement)
N_cmp_h = 300
samp_hcoupled = []
for _ in range(N_cmp_h):
    times, _, _, _, _ = simulated_coupled_hawkes_processes(2.0, 2.0, 0.5, 1.0,
                                                            lambda_plus_a=LAMBDA_PLUS,
                                                            lambda_plus_b=LAMBDA_PLUS,
                                                            q_0_a=Q_0, q_0_b=Q_0)
    samp_hcoupled.append(times[-1])
samp_hcoupled = np.array(samp_hcoupled)

results["comparison"] = {
    "poisson_one":    {"mean": float(samp_poisson.mean()),  "std": float(samp_poisson.std(ddof=1)),
                       "q25": float(np.quantile(samp_poisson, 0.25)),
                       "median": float(np.median(samp_poisson)),
                       "q75": float(np.quantile(samp_poisson, 0.75))},
    "first_of_two":   {"mean": float(samp_first2.mean()),   "std": float(samp_first2.std(ddof=1)),
                       "q25": float(np.quantile(samp_first2, 0.25)),
                       "median": float(np.median(samp_first2)),
                       "q75": float(np.quantile(samp_first2, 0.75))},
    "hawkes_one":     {"mean": float(samp_hawkes.mean()),   "std": float(samp_hawkes.std(ddof=1)),
                       "q25": float(np.quantile(samp_hawkes, 0.25)),
                       "median": float(np.median(samp_hawkes)),
                       "q75": float(np.quantile(samp_hawkes, 0.75))},
    "hawkes_coupled": {"mean": float(samp_hcoupled.mean()), "std": float(samp_hcoupled.std(ddof=1)),
                       "q25": float(np.quantile(samp_hcoupled, 0.25)),
                       "median": float(np.median(samp_hcoupled)),
                       "q75": float(np.quantile(samp_hcoupled, 0.75))},
}
for k, v in results["comparison"].items():
    print(f"   {k:14s} : mean={v['mean']:.3f}  std={v['std']:.3f}  median={v['median']:.3f}")

fig, ax = plt.subplots(figsize=(10, 6))
bins = np.linspace(0, max(samp_poisson.max(), samp_hawkes.max(),
                          samp_first2.max(), samp_hcoupled.max()), 60)
ax.hist(samp_poisson, bins=bins, density=True, alpha=0.55, label="Poisson individuel")
ax.hist(samp_first2,  bins=bins, density=True, alpha=0.55, label="Premier des 2 Poisson")
ax.hist(samp_hawkes,  bins=bins, density=True, alpha=0.55, label="Hawkes individuel")
ax.hist(samp_hcoupled,bins=bins, density=True, alpha=0.55, label="Hawkes couplé")
ax.set_xlabel(r"$\tau$"); ax.set_ylabel("Densité")
ax.set_title("Comparaison des distributions de temps d'arrêt")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "comparison.png"), dpi=130)
plt.close(fig)


# ===========================================================================
# 7) Trajectoire (q_b, q_a) et trajectoires individuelles
# ===========================================================================
print("[7] Figures de trajectoires")
times_b, q_b_values, times_a, q_a_values = simulate_poisson_process_until_zero(
    LAMBDA_PLUS, LAMBDA_MINUS)

fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
axes[0].step(times_a, q_a_values, where="post", color="tab:blue")
axes[0].set_ylabel("$q_a$"); axes[0].set_title("Trajectoire $q_a$ (ask)")
axes[0].grid(alpha=0.3)
axes[1].step(times_b, q_b_values, where="post", color="tab:orange")
axes[1].set_ylabel("$q_b$"); axes[1].set_xlabel("Temps"); axes[1].set_title("Trajectoire $q_b$ (bid)")
axes[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "trajectories.png"), dpi=130)
plt.close(fig)

# Approximation gaussienne a t=T
print("[8] Approximation gaussienne du processus a l'instant T")
N_apx = 5000
samples_T = np.empty(N_apx)
for k in range(N_apx):
    q = Q_0_A; t = 0.0
    while t < T:
        dt = np.random.exponential(1.0 / (LAMBDA_PLUS + LAMBDA_MINUS))
        t += dt
        q += 1 if np.random.rand() < LAMBDA_PLUS / (LAMBDA_PLUS + LAMBDA_MINUS) else -1
    samples_T[k] = q

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(samples_T, bins="auto", density=True, alpha=0.6, color="g", label="Simulation Poisson")
xx = np.linspace(samples_T.min(), samples_T.max(), 300)
mean_g = Q_0_A + (LAMBDA_PLUS - LAMBDA_MINUS) * T
std_g = np.sqrt((LAMBDA_PLUS + LAMBDA_MINUS) * T)
ax.plot(xx, sps.norm.pdf(xx, loc=mean_g, scale=std_g), "r-", lw=2,
        label=f"$\\mathcal{{N}}({mean_g:.0f}, {std_g**2:.0f})$")
ax.set_xlabel("$q(T)$"); ax.set_ylabel("Densité")
ax.set_title(rf"Distribution de $q(T)$ vs gaussienne théorique (T={T}, $q_0$={Q_0_A})")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "gaussian_approx.png"), dpi=130)
plt.close(fig)

results["gaussian_approx"] = {
    "mean_th": float(mean_g), "mean_emp": float(samples_T.mean()),
    "std_th": float(std_g),    "std_emp": float(samples_T.std(ddof=1)),
}


# ===========================================================================
# Sauvegarde JSON
# ===========================================================================
with open(os.path.join(OUT_DIR, "results.json"), "w") as f:
    json.dump(results, f, indent=2, default=float)

print("\n=== TERMINE ===")
print(f"Figures sauvegardees dans : {FIG_DIR}")
print(f"Resultats JSON           : {os.path.join(OUT_DIR, 'results.json')}")
