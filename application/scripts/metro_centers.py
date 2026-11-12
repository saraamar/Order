"""Population-weighted centre of each candidate metro from 2020 county centres of population (2023 CBSA delineation)."""
import pandas as pd, csv
rows = [r for r in csv.DictReader(open('raw/cbsa.csv', encoding='latin-1')) if r['LSAD'] == 'County or equivalent']
c2m = pd.DataFrame([{'CBSA': r['CBSA'], 'GEOID': r['STCOU']} for r in rows])
cands = pd.read_csv('raw/site_criteria_16.csv', dtype={'CBSA': str})[['CBSA', 'Metro']]
cp = pd.read_csv('raw/CenPop2020_Mean_CO.txt', dtype={'STATEFP': str, 'COUNTYFP': str}, encoding='utf-8-sig')
cp['GEOID'] = cp.STATEFP + cp.COUNTYFP
m = cands.merge(c2m, on='CBSA').merge(cp, on='GEOID')
g = m.groupby(['CBSA', 'Metro']).apply(lambda d: pd.Series({
    'n_counties': len(d), 'pop_2020': d.POPULATION.sum(),
    'lat': (d.LATITUDE * d.POPULATION).sum() / d.POPULATION.sum(),
    'lon': (d.LONGITUDE * d.POPULATION).sum() / d.POPULATION.sum()}), include_groups=False).reset_index()
g.to_csv('raw/metro_centers.csv', index=False); print(g.round(4).to_string(index=False))
