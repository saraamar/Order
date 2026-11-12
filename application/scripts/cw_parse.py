"""Extract asking rents, vacancy and inventory for the candidate markets from the Cushman & Wakefield
U.S. Industrial MarketBeat Q3 2026 national report (raw/q32026usindustrialmarketbeat.pdf) into raw/cw_q3_2026.json.
Rent columns: Q3 2025 .. Q3 2026 overall, Q3 2026 warehouse/distribution (W/D), Q3 2026 manufacturing."""
import fitz, re, json
d = fitz.open('raw/q32026usindustrialmarketbeat.pdf')
def parse(page, nvals):
    t = [x.strip() for x in d[page].get_text().split('\n') if x.strip()]
    out = {}
    for i, x in enumerate(t):
        vals = t[i + 1:i + 1 + nvals]
        if len(vals) == nvals and all(re.match(r'^(\$?[\d,\.]+%?|n/a)$', v) for v in vals) and not re.match(r'^[\$\d]', x):
            out[x] = vals
    return out
vac, rent, inv = parse(3, 5), parse(4, 7), parse(5, 3)   # report pages 4 (vacancy), 5 (asking rents), 6 (inventory)
names = ['Chicago', 'Detroit', 'Minneapolis', 'St. Louis', 'Cincinnati', 'Kansas City', 'Columbus', 'Indianapolis', 'Cleveland',
         'Milwaukee', 'Louisville', 'Grand Rapids', 'Omaha', 'Dayton', 'Des Moines', 'Madison', 'Akron', 'Wichita', 'Toledo', 'Pittsburgh']
res = {}
for n in names:
    pick = lambda tab: next((v for k, v in tab.items() if k.startswith(n)), None)
    res[n] = dict(rent=pick(rent), vac=pick(vac), inv=pick(inv))
json.dump(res, open('raw/cw_q3_2026.json', 'w'))
print({k: (v['rent'][5] if v['rent'] else None) for k, v in res.items()})
