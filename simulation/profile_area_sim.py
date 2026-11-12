"""
Paper 1 pilot simulation: ordering dependence in profile-area multicriteria scores.

Profile-area method (as studied in the paper):
  - criteria are placed on an axis in an order pi;
  - node positions: x_1 = 0, x_k = x_{k-1} + w_{pi(k)}  (gap before a criterion = its weight);
  - an alternative's ratings are joined by an interpolating curve (piecewise linear,
    Lagrange polynomial, or natural cubic spline);
  - its score is the (signed) area under that curve.

For all three interpolants the signed area is linear in the ratings:
  S(a | pi) = sum_k q_k(pi) * y_{a, pi(k)},
where q(pi) are the quadrature weights of the interpolant on the nodes x(pi).
So each ordering induces "effective weights" q(pi), computed once per ordering.

Outputs (per number of criteria n, number of alternatives m, interpolant):
  unstable   share of problems where the winner changes across orderings
  n_winners  mean number of distinct winners across orderings
  p_diff_ws  share of (problem, ordering) pairs whose winner differs from the weighted-sum winner
  tau_ws     mean Kendall tau between the ordering's ranking and the weighted-sum ranking
  neg_q      share of orderings with at least one negative effective weight (monotonicity failure)
  avg_diff   share of problems where the order-averaged winner differs from the weighted-sum winner

Run:  python profile_area_sim.py  [instances_per_cell]   (default 1000; seed fixed)
"""
import sys, itertools, math
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.stats import kendalltau

RNG = np.random.default_rng(20261111)


def node_positions(w_ordered):
    return np.concatenate([[0.0], np.cumsum(w_ordered[1:])])


def q_linear(x):
    q = np.zeros(len(x))
    d = np.diff(x)
    q[:-1] += d / 2
    q[1:] += d / 2
    return q


def q_lagrange(x):
    # Interpolatory quadrature: solve V^T q = moments, on x scaled to [0, 1] for conditioning
    L = x[-1] - x[0]
    t = (x - x[0]) / L
    n = len(t)
    V = np.vander(t, n, increasing=True)          # V[k, j] = t_k^j
    moments = 1.0 / np.arange(1, n + 1)            # integral of t^j over [0, 1]
    return np.linalg.solve(V.T, moments) * L


def q_spline(x):
    # Integrate the natural cubic spline of each unit vector (all at once)
    return CubicSpline(x, np.eye(len(x)), bc_type="natural").integrate(x[0], x[-1])


INTERPOLANTS = {"linear": q_linear, "lagrange": q_lagrange, "spline": q_spline}


def effective_weight_matrix(w, qfun):
    """Rows = orderings, columns = criteria (original index)."""
    n = len(w)
    perms = list(itertools.permutations(range(n)))
    E = np.zeros((len(perms), n))
    for r, pi in enumerate(perms):
        q = qfun(node_positions(w[list(pi)]))
        E[r, list(pi)] = q
    return E


def run(instances=1000, ns=(3, 4, 5, 6, 7), ms=(3, 5, 10), instances_n7=300):
    rows = []
    for n in ns:
        k = instances_n7 if n >= 7 else instances
        for name, qfun in INTERPOLANTS.items():
            stats = {m: dict(unstable=0, n_winners=0.0, p_diff_ws=0.0, tau_ws=0.0, neg_q=0.0, avg_diff=0) for m in ms}
            for _ in range(k):
                w = RNG.dirichlet(np.ones(n))
                E = effective_weight_matrix(w, qfun)
                negq = np.mean((E < -1e-12).any(axis=1))
                Ebar = E.mean(axis=0)
                cols = range(0, E.shape[0], max(1, E.shape[0] // 50))
                for m in ms:
                    Y = RNG.integers(1, 10, size=(m, n)).astype(float)   # ratings on a 1-9 scale
                    S = Y @ E.T
                    ws = Y @ w
                    win = S.argmax(axis=0)
                    ws_win = ws.argmax()
                    st = stats[m]
                    st["unstable"] += len(set(win)) > 1
                    st["n_winners"] += len(set(win))
                    st["p_diff_ws"] += np.mean(win != ws_win)
                    st["tau_ws"] += np.nanmean([kendalltau(S[:, r], ws)[0] for r in cols])
                    st["neg_q"] += negq
                    st["avg_diff"] += (Y @ Ebar).argmax() != ws_win
            for m in ms:
                rows.append(dict(n=n, m=m, interpolant=name, instances=k,
                                 **{key: v / k for key, v in stats[m].items()}))
                print(rows[-1], flush=True)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    df = run(k)
    df.to_csv("results/pilot_results.csv", index=False)
    print(df.round(3).to_string(index=False))
