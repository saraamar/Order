"""
Paper 1, Section 6: full simulation of ordering dependence in profile-area multicriteria scores.

Changes from the pilot (profile_area_sim.py, kept unchanged):
  * ratings are continuous, uniform on [1, 9], so ties between alternatives have probability zero;
  * besides the signed area S, the distance-to-target score D is simulated, with target rating 9 on every
    criterion (the best level of the scale). Every interpolant reproduces constants, so the target profile
    is the constant 9 and D(a | pi) = integral of |9 - f_a(x)| dx, computed on a fine grid. Lower D is better.
    For the piecewise-linear profile, D = 9 * span - S (Remark in Section 3.4), so it ranks exactly as S.

Design: n = 3..7 criteria, m = 3, 5, 10 alternatives, 1000 problems per (n, interpolant)
(300 for n = 7), weights ~ Dirichlet(1), cumulative-weight node rule, every ordering evaluated.

Measures per (n, m, interpolant, score):
  unstable   share of problems in which the top-ranked alternative changes across orderings
  n_winners  mean number of distinct top-ranked alternatives across orderings
  p_diff_ws  share of (problem, ordering) pairs whose top-ranked alternative differs from the weighted sum's
  tau_ws     mean Kendall tau between an ordering's ranking and the weighted-sum ranking
             (averaged over an evenly spaced subset of at most 60 orderings per problem)
  neg_q      share of orderings with at least one negative effective weight (S only; property of the nodes)
  avg_diff   share of problems in which the order-averaged score picks a different winner from the weighted sum

Run:  python profile_area_sim_full.py [instances]     (default 1000; seed fixed)
"""
import sys, itertools, time
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.stats import kendalltau

RNG = np.random.default_rng(20261112)
G = 401                                   # grid points for the D integral


def nodes(w_ordered):
    return np.concatenate([[0.0], np.cumsum(w_ordered[1:])])


def basis(x, kind, t):
    """Cardinal functions of the interpolant on nodes x, evaluated at grid t: shape (len(t), n)."""
    n = len(x)
    if kind == "linear":
        return np.stack([np.interp(t, x, np.eye(n)[k]) for k in range(n)], axis=1)
    if kind == "lagrange":
        L = x[-1] - x[0]
        s, u = (x - x[0]) / L, (t - x[0]) / L
        V = np.vander(s, n, increasing=True)
        return np.vander(u, n, increasing=True) @ np.linalg.inv(V)
    return CubicSpline(x, np.eye(n), bc_type="natural")(t)


def quad_weights(x, kind):
    n = len(x)
    if kind == "linear":
        d = np.diff(x); q = np.zeros(n); q[:-1] += d / 2; q[1:] += d / 2; return q
    if kind == "lagrange":
        L = x[-1] - x[0]; s = (x - x[0]) / L
        return np.linalg.solve(np.vander(s, n, increasing=True).T, 1.0 / np.arange(1, n + 1)) * L
    return CubicSpline(x, np.eye(n), bc_type="natural").integrate(x[0], x[-1])


def ordering_data(w, kind):
    """Effective weights E (orderings x criteria) and, per ordering, grid basis with columns in criterion order."""
    n = len(w)
    perms = list(itertools.permutations(range(n)))
    E = np.zeros((len(perms), n)); B = []; H = []
    for r, pi in enumerate(perms):
        x = nodes(w[list(pi)])
        E[r, list(pi)] = quad_weights(x, kind)
        t = np.linspace(x[0], x[-1], G)
        Phi = np.zeros((G, n)); Phi[:, list(pi)] = basis(x, kind, t)
        B.append(Phi); H.append(t[1] - t[0])
    return E, np.stack(B), np.array(H)


def measures(scores, ws, higher_better, cols):
    """scores: (m, orderings)."""
    sgn = 1 if higher_better else -1
    win = (sgn * scores).argmax(axis=0)
    ws_win = ws.argmax()
    tau = np.nanmean([kendalltau(sgn * scores[:, r], ws)[0] for r in cols])
    avg = (sgn * scores.mean(axis=1)).argmax()
    return dict(unstable=float(len(set(win)) > 1), n_winners=len(set(win)), p_diff_ws=np.mean(win != ws_win),
                tau_ws=tau, avg_diff=float(avg != ws_win))


def run(instances=1000, ns=(3, 4, 5, 6, 7), ms=(3, 5, 10), instances_n7=300):
    rows = []
    for n in ns:
        k = instances_n7 if n >= 7 else instances
        for kind in ("linear", "lagrange", "spline"):
            t0 = time.time()
            acc = {}
            for _ in range(k):
                w = RNG.dirichlet(np.ones(n))
                E, B, H = ordering_data(w, kind)
                negq = np.mean((E < -1e-12).any(axis=1))
                cols = np.unique(np.linspace(0, E.shape[0] - 1, min(60, E.shape[0])).astype(int))
                for m in ms:
                    Y = RNG.uniform(1, 9, size=(m, n))
                    ws = Y @ w
                    S = Y @ E.T                                            # (m, orderings)
                    F = np.einsum("rgn,mn->mrg", B, Y)                     # profiles on the grid
                    D = np.trapezoid(np.abs(9.0 - F), dx=H[None, :, None], axis=2) if hasattr(np, "trapezoid") \
                        else np.trapz(np.abs(9.0 - F), dx=H[None, :, None], axis=2)
                    for score, vals, hb in (("S", S, True), ("D", D, False)):
                        r = measures(vals, ws, hb, cols)
                        r["neg_q"] = negq if score == "S" else np.nan
                        a = acc.setdefault((m, score), {key: 0.0 for key in r})
                        for key, v in r.items(): a[key] += v
            for (m, score), a in acc.items():
                rows.append(dict(n=n, m=m, interpolant=kind, score=score, instances=k, **{key: v / k for key, v in a.items()}))
            print(f"n={n} {kind}: {time.time() - t0:.0f}s", flush=True)
            pd.DataFrame(rows).to_csv("results/full_results.csv", index=False)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    df = run(k)
    df.to_csv("results/full_results.csv", index=False)
    print(df.round(3).to_string(index=False))
