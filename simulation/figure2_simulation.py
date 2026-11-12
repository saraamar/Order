"""Figure 2: share of orderings whose winner differs from the weighted-sum winner (full simulation)."""
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Arial', 'font.size': 9})
d = pd.read_csv('results/full_results.csv')
sty = {'linear': ('black', 'o', 'Piecewise linear (L)'), 'lagrange': ('#1f4e79', 's', 'Lagrange polynomial (P)'),
       'spline': ('#b04a00', '^', 'Natural cubic spline (S)')}
fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.9), dpi=300, sharey=True)
for k, (c, mk, lab) in sty.items():
    for sc, ls in (('S', '-'), ('D', '--')):
        if k == 'linear' and sc == 'D': continue
        x = d[(d.interpolant == k) & (d.score == sc) & (d.m == 5)]
        axs[0].plot(x.n, 100 * x.p_diff_ws, ls=ls, color=c, marker=mk, ms=4, mfc='white' if sc == 'D' else c,
                    label=f'{lab}, {"signed area" if sc == "S" else "distance to target"}')
    x = d[(d.interpolant == k) & (d.score == 'S') & (d.n == 5)]
    axs[1].plot(x.m, 100 * x.p_diff_ws, color=c, marker=mk, ms=4)
axs[0].set_xlabel('Number of criteria, n'); axs[0].set_xticks(range(3, 8)); axs[0].set_title('(a) m = 5 alternatives', fontsize=9)
axs[1].set_xlabel('Number of alternatives, m'); axs[1].set_xticks([3, 5, 10]); axs[1].set_title('(b) n = 5 criteria, signed area', fontsize=9)
axs[0].set_ylabel('Orderings whose winner differs\nfrom the weighted sum (%)'); axs[0].set_ylim(0, 80)
for a in axs:
    for sp in ('top', 'right'): a.spines[sp].set_visible(False)
fig.legend(*axs[0].get_legend_handles_labels(), frameon=False, loc='lower center', ncol=2, fontsize=7.5, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.17, 1, 1)); fig.savefig('results/figure2_simulation.png')
