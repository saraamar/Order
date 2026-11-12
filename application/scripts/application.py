"""Section 7: profile-area scores for 16 Midwest metros under every ordering of six criteria.
Run from the site_data folder. Outputs go to site_data/results/."""
import itertools, os, json
import numpy as np, pandas as pd
from scipy.interpolate import CubicSpline
from scipy.stats import kendalltau

os.makedirs('results', exist_ok=True)
df = pd.read_excel('Paper1_Site_Criteria_Data.xlsx', sheet_name='Criteria by metro', dtype={'CBSA': str})
CRIT = [  # code, column, label, direction (+1 benefit, -1 cost)   -- order = importance ranking ("market first")
    ('C7', 'C7 Food demand within 250 road miles (M tons/yr)', 'Food demand within 250 mi', +1),
    ('C1', 'C1 W/D asking rent Q3 2026 ($/sf/yr)', 'Warehouse rent', -1),
    ('C2', 'C2 Warehouse laborer mean wage May 2025 ($/hr)', 'Laborer wage', -1),
    ('C5', 'C5 Interstate miles inside metro', 'Interstate miles', +1),
    ('C3', 'C3 Warehouse laborer employment May 2025', 'Warehouse employment', +1),
    ('C4', 'C4 Unemployment rate, 12-mo avg Oct25-Sep26 (%)', 'Unemployment rate', +1)]
n = len(CRIT)
w = np.array([sum(1 / j for j in range(k, n + 1)) / n for k in range(1, n + 1)])   # rank-order centroid
metros = df.Metro.tolist(); m = len(metros)
raw = np.column_stack([df[c[1]].astype(float).values for c in CRIT])
Y = np.empty_like(raw)
for j, (_, _, _, d) in enumerate(CRIT):
    lo, hi = raw[:, j].min(), raw[:, j].max()
    z = (raw[:, j] - lo) / (hi - lo)
    Y[:, j] = 1 + 8 * (z if d > 0 else 1 - z)
pd.DataFrame(Y, index=metros, columns=[c[0] for c in CRIT]).round(2).to_csv('results/ratings_1to9.csv')

def nodes(wo): return np.concatenate([[0.0], np.cumsum(wo[1:])])
def qw(x, kind):
    k = len(x)
    if kind == 'L':
        d = np.diff(x); q = np.zeros(k); q[:-1] += d / 2; q[1:] += d / 2; return q
    if kind == 'P':
        L = x[-1] - x[0]; s = (x - x[0]) / L
        return np.linalg.solve(np.vander(s, k, increasing=True).T, 1.0 / np.arange(1, k + 1)) * L
    return CubicSpline(x, np.eye(k), bc_type='natural').integrate(x[0], x[-1])

perms = list(itertools.permutations(range(n)))
ws = Y @ w
ws_rank = (-ws).argsort().argsort() + 1
out = {'weights': dict(zip([c[0] for c in CRIT], w.round(4).tolist())), 'ws_winner': metros[int(ws.argmax())]}
summary = []
for kind in ('L', 'P', 'S'):
    E = np.zeros((len(perms), n))
    for r, pi in enumerate(perms):
        E[r, list(pi)] = qw(nodes(w[list(pi)]), kind)
    S = Y @ E.T                                         # (m, orderings)
    win = S.argmax(axis=0)
    ranks = (-S).argsort(axis=0).argsort(axis=0) + 1    # rank of each metro under each ordering
    taus = np.array([kendalltau(S[:, r], ws)[0] for r in range(len(perms))])
    avg = S.mean(axis=1)
    wins = pd.Series(win).value_counts()
    for i, name in enumerate(metros):
        summary.append(dict(interpolant=kind, metro=name, ws_score=round(ws[i], 3), ws_rank=int(ws_rank[i]),
                            share_orderings_first=round(100 * wins.get(i, 0) / len(perms), 1),
                            best_rank=int(ranks[i].min()), worst_rank=int(ranks[i].max()),
                            median_rank=float(np.median(ranks[i])),
                            avg_score_rank=int(((-avg).argsort().argsort() + 1)[i])))
    out[kind] = dict(n_distinct_winners=int(len(set(win))), share_ws_winner_first=round(100 * np.mean(win == ws.argmax()), 1),
                     tau_min=round(taus.min(), 3), tau_median=round(float(np.median(taus)), 3), tau_max=round(taus.max(), 3),
                     share_orderings_neg_weight=round(100 * np.mean((E < -1e-12).any(axis=1)), 1),
                     avg_winner=metros[int(avg.argmax())],
                     winners={metros[int(i)]: round(100 * c / len(perms), 1) for i, c in wins.items()})
    if kind == 'L':   # check Proposition 5 numerically
        lam = (n - 2) / (2 * (n - 1)); e_tilde = lam * w / w.sum() + (1 - lam) / n
        out['L']['prop5_max_abs_err'] = float(np.abs(E.mean(axis=0) / E.mean(axis=0).sum() - e_tilde).max())
        out['L']['averaged_weights'] = dict(zip([c[0] for c in CRIT], e_tilde.round(4).tolist()))
        # best and worst ordering for the WS winner
        i0 = int(ws.argmax()); rbest, rworst = int(ranks[i0].argmin()), int(ranks[i0].argmax())
        out['L']['ws_winner_rank_range'] = [int(ranks[i0].min()), int(ranks[i0].max())]
        out['L']['ordering_ws_winner_worst'] = [CRIT[j][0] for j in perms[rworst]]

# Choquet integrals with 2-additive capacities whose Shapley values equal w (overall importance unchanged).
# Mobius masses: m_i = w_i - I/2 for the two criteria of the pair, m_pair = I.  Monotone iff m_i >= 0 and m_i + I >= 0.
codes = [c[0] for c in CRIT]
def capacity(a, b, I):
    ia, ib = codes.index(a), codes.index(b)
    mob = {frozenset([i]): w[i] for i in range(n)}
    mob[frozenset([ia])] -= I / 2; mob[frozenset([ib])] -= I / 2; mob[frozenset([ia, ib])] = I
    assert min(mob[frozenset([ia])], mob[frozenset([ib])]) >= -1e-12 and min(mob[frozenset([ia])], mob[frozenset([ib])]) + I >= -1e-12
    return mob
def choquet(y, mob):
    mu = lambda T: sum(v for k, v in mob.items() if k <= T)
    order = np.argsort(y); prev = 0.0; s = 0.0
    for k, i in enumerate(order):
        s += (y[i] - prev) * mu(frozenset(order[k:].tolist())); prev = y[i]
    return s
CAPS = {'complementarity C7-C5': ('C7', 'C5', +w[codes.index('C5')]),            # demand and highway access reinforce
        'redundancy C3-C4': ('C3', 'C4', -2 * min(w[codes.index('C3')], w[codes.index('C4')]))}  # largest monotone value
out['choquet'] = {}
summ = pd.DataFrame(summary)
for label, (a, b, I) in CAPS.items():
    ch = np.array([choquet(Y[i], capacity(a, b, I)) for i in range(m)])
    out['choquet'][label] = dict(interaction=round(I, 4), winner=metros[int(ch.argmax())],
                                 ranking=[metros[i] for i in (-ch).argsort()], tau_vs_ws=round(kendalltau(ch, ws)[0], 3))
    summ['choquet_rank ' + label] = summ.metro.map(dict(zip(metros, (-ch).argsort().argsort() + 1)))
summ.to_csv('results/application_summary.csv', index=False)
json.dump(out, open('results/application_results.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
print(summ[summ.interpolant == 'L'].sort_values('ws_rank').to_string(index=False))
