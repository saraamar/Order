"""Figure 3: range of ranks of each metro across the 720 orderings (piecewise-linear and polynomial profiles)."""
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Arial', 'font.size': 9})
s = pd.read_csv('results/application_summary.csv')
L = s[s.interpolant == 'L'].sort_values('ws_rank'); P = s[s.interpolant == 'P'].set_index('metro')
fig, ax = plt.subplots(figsize=(6, 4.6), dpi=300)
for i, r in enumerate(L.itertuples()):
    y = len(L) - 1 - i
    ax.plot([P.loc[r.metro, 'best_rank'], P.loc[r.metro, 'worst_rank']], [y - 0.18] * 2, color='#9db7cf', lw=3, solid_capstyle='butt')
    ax.plot([r.best_rank, r.worst_rank], [y + 0.18] * 2, color='black', lw=3, solid_capstyle='butt')
    ax.plot(r.ws_rank, y + 0.18, 'o', ms=5, mfc='white', mec='#b04a00', mew=1.6, zorder=5)
ax.set_yticks(range(len(L))); ax.set_yticklabels(list(L.metro)[::-1])
ax.set_xticks(range(1, 17)); ax.set_xlim(0.5, 16.5); ax.invert_xaxis()
ax.set_xlabel('Rank (1 = best)')
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
h = [plt.Line2D([], [], color='black', lw=3), plt.Line2D([], [], color='#9db7cf', lw=3),
     plt.Line2D([], [], marker='o', ls='', mfc='white', mec='#b04a00', mew=1.6)]
ax.legend(h, ['Range over orderings, piecewise linear (L)', 'Range over orderings, Lagrange polynomial (P)', 'Weighted-sum rank'],
          frameon=False, loc='lower center', bbox_to_anchor=(0.45, 1.0), ncol=2, fontsize=8)
fig.tight_layout(); fig.savefig('results/figure3_rank_ranges.png')
